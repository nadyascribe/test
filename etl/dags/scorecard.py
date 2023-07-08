import csv
import gzip
import json
from datetime import datetime, timedelta

import airflow
import pandas as pd
from airflow import DAG
from airflow.decorators import task_group, task
from airflow.providers.google.cloud.transfers.bigquery_to_gcs import BigQueryToGCSOperator

from dags.base import google_cloud as base_google_cloud
from dags.storage import get_hook as get_storage_hook
from dags.storage.models.osint import Scorecard
from dags.tools import notify_slack
from dags.tools.airflow import schedule_only_for_cloud
from dags.tools.fs import change_extension
from dags.tools.google_cloud import gcs

assert airflow  # make file parsable by airflow

bq_get_data_query = """SELECT date, repo.name, score, checks
FROM `openssf.scorecardcron.scorecard-export-weekly-json`"""


import_sql_query = """
        COPY {schema}."{tablename}" 
        ("date", "repo_name","score", "extra") 
        FROM stdin 
        WITH (format CSV, header {header}, delimiter '{delimiter}')
    """.format(
    schema=Scorecard.__table__.schema,
    tablename=Scorecard.__tablename__,
    header=True,
    delimiter=",",
)


dataset_name = "scorecard"
result_query_table_name = "{{ ts_nodash | lower }}"


@task(max_active_tis_per_dag=1)
def export(file_name):
    df = pd.read_json(file_name, lines=True)
    df["checks_json"] = df.checks.apply(json.dumps)
    cvs_file = change_extension(file_name, "csv.gz")
    df.to_csv(
        cvs_file,
        compression="gzip",
        index=False,
        quoting=csv.QUOTE_ALL,
        columns=["date", "name", "score", "checks_json"],
    )
    with gzip.open(cvs_file, "rt") as file:
        with get_storage_hook().get_conn() as conn:
            with conn.cursor() as curs:
                curs.execute("begin")
                chunk_size = getattr(file, "_CHUNK_SIZE", 1024)
                tablename = '{}."{}"'.format(Scorecard.__table__.schema, Scorecard.__tablename__)
                curs.execute(f"truncate table {tablename}")
                curs.copy_expert(import_sql_query, file, chunk_size)
                curs.execute("commit")


@task_group()
def process_object(obj_name):
    ensure_fs_task = base_google_cloud.ensure_fs(object_name=obj_name)
    base_google_cloud.download_task(
        object_name=obj_name, bucket=base_google_cloud.default_bucket_template, filename=ensure_fs_task
    ) >> export(file_name=ensure_fs_task)


with DAG(
    dag_id="import_scorecard",
    start_date=datetime(2023, 3, 22),
    schedule=schedule_only_for_cloud(timedelta(days=1)),
    catchup=False,
    max_active_runs=1,
    max_active_tasks=1,
    default_args={
        "on_failure_callback": notify_slack.notify_failure,
    },
) as dag:
    bq_run_query = base_google_cloud.make_bq_query_task(bq_get_data_query, dataset_name, result_query_table_name)
    export_to_bucket = BigQueryToGCSOperator(
        source_project_dataset_table=f"{dataset_name}.{result_query_table_name}",
        destination_cloud_storage_uris=[f"gs://{base_google_cloud.default_bucket_template}/scorecard-*.jsonl.gz"],
        export_format="NEWLINE_DELIMITED_JSON",
        task_id="export_to_bucket",
        gcp_conn_id=gcs.get_conn_id(),
        compression="GZIP",
        deferrable=False,
    )
    create_bucket = base_google_cloud.make_create_bucket_task(base_google_cloud.default_bucket_template)
    create_dataset = base_google_cloud.make_create_dataset_task(dataset_name)
    list_objects = base_google_cloud.make_list_objects_task(base_google_cloud.default_bucket_template)
    delete_bucket = base_google_cloud.make_delete_bucket(base_google_cloud.default_bucket_template)
    delete_table = base_google_cloud.delete_bq_table_task(dataset_name, result_query_table_name)

    check_branch_task = base_google_cloud.check_branch()

    create = [create_bucket, create_dataset]
    check_branch_task >> create
    create >> bq_run_query >> export_to_bucket
    export_to_bucket >> list_objects

    check_branch_task >> list_objects

    (
        process_object.expand(obj_name=list_objects)
        >> base_google_cloud.approve_cleanup()
        >> [base_google_cloud.delete_files(), delete_bucket, delete_table]
    )
