import airflow
from datetime import datetime

from airflow.decorators import task

from dags.base import google_cloud as base_google_cloud
from dags.storage.models.asbom import LatestPackageVersions
from dags.storage.models.osint import PackageToVersion
from dags.storage.sqla_utils import refresh_view
from dags.tools import notify_slack

assert airflow  # make file parsable by airflow

bq_get_data_query = """
        SELECT
          *
        FROM `{{ var.value.gcs_package_version_to_project_source }}`
        WHERE
          SnapshotAt = (
          SELECT
            MAX(Time)
          FROM
            `bigquery-public-data.deps_dev_v1.Snapshots`)
        """

db_import_sql = """
COPY osint."{0}" 
("snapshotAt","system","name","version","project_type","project_name") 
FROM stdin 
WITH (format CSV, header {1}, delimiter '{2}')
""".format(
    PackageToVersion.__tablename__, True, ","
)

dataset_name = "packageToVersion"
result_query_table_name = "{{ ts_nodash | lower }}"


@task
def refresh_view_task():
    schema = LatestPackageVersions.__table__.schema
    refresh_view(schema, LatestPackageVersions.__tablename__)


dag = base_google_cloud.make_dag(
    dag_id="import_package_to_version",
    start_date=datetime(2023, 3, 22),
    schedule=None,
    bq_query=bq_get_data_query,
    bq_destination_dataset=dataset_name,
    bq_destination_table=result_query_table_name,
    db_query=db_import_sql,
    on_failure_callback=notify_slack.notify_failure,
)
