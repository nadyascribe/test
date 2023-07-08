"""
Module provides `make_dag` function.
It creates a DAG for importing data from BigQuery to project's using database (postgres)

You can specify environment variables to change default behavior:
* CLOUD_IMPORTS_LIMIT - limit number of rows to import from BigQuery;
    by default task name of BQ query is `bq_run_query`;
    if `CLOUD_IMPORTS_LIMIT` is specified then task name is `bq_run_query_limited`;
    please use it as a mark for local dag execution
* WITHOUT_CLEANUP - if set to any non-false value then all downloaded files, then downloaded files, created BQ table
    and bucket will be deleted after import; don't forget to cleanup cloud manually.

All these variables are set in etl/.env.
"""
import gzip
import json
import logging
import os.path
from pathlib import Path
from typing import Optional, NoReturn

from airflow import DAG
from airflow.decorators import task, task_group
from airflow.models import Variable, DagRun
from airflow.models.abstractoperator import TaskStateChangeCallback
from airflow.providers.google.cloud.operators.bigquery import (
    BigQueryCreateEmptyDatasetOperator,
    BigQueryInsertJobOperator,
)
from airflow.providers.google.cloud.operators.gcs import (
    GCSCreateBucketOperator,
)
from airflow.providers.google.cloud.transfers.bigquery_to_gcs import (
    BigQueryToGCSOperator,
)
from airflow.utils.trigger_rule import TriggerRule

from dags.storage import get_hook as get_storage_hook
from dags.tools import env, fs
from dags.tools.google_cloud import gcs

logger = logging.getLogger("airflow.task")

GCP_CONN_ID = gcs.get_conn_id()


def get_max_active_cpu_bound_tasks() -> Optional[int | NoReturn]:
    if env.is_local():
        return 0
    return 2
    # otherwise default global value is used


def _directory(subdir):
    return os.path.join(Variable.get("shared_directory"), subdir)


def file_name_for_object(subdir, object_name):
    """
    Separated function only for testing and mock purposes
    :param object_name:
    :return:
    """
    return os.path.join(_directory(subdir), object_name)


@task(task_id="ensure_fs")
def ensure_fs(object_name, dag: DAG | None = None, dag_run: DagRun | None = None):
    assert dag is not None
    assert dag_run is not None
    directory = _directory(Path(dag.dag_id) / str(dag_run.id))
    filename = file_name_for_object(directory, object_name)
    fs.ensure_directory_for_filepath(filename)
    return filename


@task(task_id="export_to_db", max_active_tis_per_dag=1)
def export_to_db(sql, file_name):
    with gzip.open(file_name, "rt") as file:
        with get_storage_hook().get_conn() as conn:
            with conn.cursor() as curs:
                curs.execute("begin")
                chunk_size = getattr(file, "_CHUNK_SIZE", 1024)
                curs.copy_expert(sql, file, chunk_size)
                curs.execute("commit")


@task(task_id="download_task", max_active_tis_per_dag=get_max_active_cpu_bound_tasks())
def download_task(object_name, bucket, filename, dag_run: DagRun | None = None):
    assert dag_run
    bucket = dag_run.conf.get("bucket_name") or bucket

    hook = gcs.get_hook()
    hook.download(bucket_name=bucket, object_name=object_name, filename=filename)


def make_group(sql, bucket):
    @task_group()
    def process_object(obj_name):
        ensure_fs_task = ensure_fs(object_name=obj_name)
        download_task(object_name=obj_name, bucket=bucket, filename=ensure_fs_task) >> export_to_db(
            sql=sql, file_name=ensure_fs_task
        )

    return process_object


@task.branch(task_id="approve_cleanup")
def approve_cleanup(dag_run: DagRun | None = None):
    assert dag_run
    if dag_run.conf.get("no_cleanup"):
        return
    if not fs.need_cleanup():
        logger.info("cleanup is skipped")
        return None

    return ["delete_bucket", "delete_files", "delete_bq_table"]


@task(task_id="delete_files")
def delete_files(dag: DAG | None = None, dag_run: DagRun | None = None):
    assert dag
    assert dag_run
    directory = _directory(Path(dag.dag_id) / str(dag_run.id))
    for dirpath, _, filenames in os.walk(directory):
        for filename in filenames:
            fs.remove_file(os.path.join(dirpath, filename))


def make_create_bucket_task(bucket):
    return GCSCreateBucketOperator(
        task_id="create_bucket",
        bucket_name=bucket,
        gcp_conn_id=GCP_CONN_ID,
    )


def make_create_dataset_task(dataset_name):
    return BigQueryCreateEmptyDatasetOperator(
        task_id="create_dataset",
        dataset_id=dataset_name,
        gcp_conn_id=GCP_CONN_ID,
    )


def make_bq_query_task(query, destination_dataset, destination_table) -> BigQueryInsertJobOperator:
    import_limits = env.cloud_imports_limit()
    task_id = "bq_run_query"
    if import_limits is not None:
        query += f" LIMIT {import_limits}"
        task_id += "_limited"
    else:
        query += """
        {{ ' LIMIT ' +  dag_run.conf.get('limit')|string  if 'limit' in dag_run.conf else '' }}
"""
    hook = gcs.get_hook()
    if not isinstance(hook.extras["keyfile_dict"], dict):
        project_id = json.loads(hook.extras["keyfile_dict"])["project_id"]
    else:
        project_id = hook.extras["keyfile_dict"]["project_id"]
    return BigQueryInsertJobOperator(
        task_id=task_id,
        configuration={
            "query": {
                "query": query,
                "destinationTable": {
                    "datasetId": destination_dataset,
                    "tableId": destination_table,
                    "projectId": project_id,
                },
                "useLegacySql": False,
                "allowLargeResults": import_limits is None,
            }
        },
        deferrable=False,
        gcp_conn_id=GCP_CONN_ID,
    )


def make_bq_to_storage_task(source_dataset, source_table, destination_bucket):
    return BigQueryToGCSOperator(
        source_project_dataset_table=f"{source_dataset}.{source_table}",
        destination_cloud_storage_uris=[f"gs://{destination_bucket}/scorecard-*.csv.gz"],
        export_format="CSV",
        task_id="export_to_bucket",
        gcp_conn_id=GCP_CONN_ID,
        compression="GZIP",
        deferrable=True,
    )


@task(task_id="list_objects", trigger_rule=TriggerRule.ONE_SUCCESS)
def make_list_objects_task(bucket, dag_run: DagRun | None = None):
    assert dag_run
    bucket = dag_run.conf.get("bucket_name") or bucket
    objects_list = dag_run.conf.get("objects_list")
    if objects_list is not None:
        return objects_list

    hook = gcs.get_hook()
    return hook.list(bucket_name=bucket)


@task
def delete_bq_table_task(dataset, table, dag_run: DagRun | None = None):
    assert dag_run
    dataset = dag_run.conf.get("dataset_name") or dataset
    table = dag_run.conf.get("table_name") or table
    hook = gcs.get_bq_hook()
    hook.delete_table(table_id=f"{dataset}.{table}")


@task
def make_delete_bucket(bucket_name, dag_run: DagRun | None = None):
    assert dag_run
    bucket_name = dag_run.conf.get("bucket_name") or bucket_name
    hook = gcs.get_hook()
    hook.delete_bucket(bucket_name=bucket_name, force=True)


default_bucket_template = "{{ dag.dag_id }}-{{ dag_run.id }}"


@task.branch
def check_branch(dag_run: DagRun | None = None):
    assert dag_run is not None
    if dag_run.conf.get("manual"):
        return "list_objects"
    import_limits = env.cloud_imports_limit()
    return ["create_bucket", "create_dataset", "bq_run_query" + ("_limited" if import_limits is not None else "")]


def make_dag(
    dag_id,
    *,
    schedule,
    start_date,
    bq_query,
    bq_destination_dataset,
    bq_destination_table,
    db_query,
    bucket: str | None = None,
    is_paused_upon_creation: bool = True,
    on_failure_callback: TaskStateChangeCallback | None = None,
):
    """
    Executing flow of the DAG:
    1. create specified BQ `bq_destination_dataset` and GCS `bucket`
    2. execute `bq_query` and save it into specified `bq_destination_dataset`.`bq_destination_table`
    3. export from `bq_destination_dataset`.`bq_destination_table` to GCS `bucket`
    4. download all objects from the `bucket`
    5. export data from downloaded objects to database using `db_query`
    6. cleanup: delete downloaded files, the `bucket` and `bq_destination_table`
    :param dag_id:
    :param schedule:
    :param start_date:
    :param bq_query: BigQuery query which result will be imported locally
    :param bq_destination_dataset: dataset name, where result of query will be saved
    :param bq_destination_table: table name, where result of query will be saved
    :param db_query: local database (Postgres) query, which is used for saving results
    :param bucket: bucket where query results will be exported
    :return:
    """
    bucket = bucket or default_bucket_template

    with DAG(
        dag_id=dag_id,
        start_date=start_date,
        schedule=schedule,
        catchup=False,
        max_active_runs=1,
        max_active_tasks=1,
        is_paused_upon_creation=is_paused_upon_creation,
        default_args={
            "on_failure_callback": on_failure_callback,
        },
    ) as dag:
        bq_run_query = make_bq_query_task(bq_query, bq_destination_dataset, bq_destination_table)
        export_to_bucket = make_bq_to_storage_task(bq_destination_dataset, bq_destination_table, bucket)
        process_object = make_group(db_query, bucket)
        create_bucket = make_create_bucket_task(bucket)
        create_dataset = make_create_dataset_task(bq_destination_dataset)
        list_objects = make_list_objects_task(bucket)
        delete_bucket = make_delete_bucket(bucket)
        delete_table = delete_bq_table_task(bq_destination_dataset, bq_destination_table)

        check_branch_task = check_branch()

        create = [create_bucket, create_dataset]
        check_branch_task >> create
        create >> bq_run_query >> export_to_bucket
        export_to_bucket >> list_objects

        check_branch_task >> list_objects

        per_object = (
            process_object.expand(obj_name=list_objects)
            >> approve_cleanup()
            >> [delete_files(), delete_bucket, delete_table]
        )
    return dag


__all__ = ["make_dag"]
