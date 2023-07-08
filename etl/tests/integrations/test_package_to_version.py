from unittest.mock import patch
import pytest
from airflow import DAG
from airflow.models import DagRun
from airflow.providers.google.cloud.operators.bigquery import (
    BigQueryCreateEmptyDatasetOperator,
    BigQueryExecuteQueryOperator,
    BigQueryInsertJobOperator,
    BigQueryDeleteTableOperator,
)
from airflow.providers.google.cloud.operators.gcs import GCSListObjectsOperator
from airflow.providers.google.cloud.transfers.bigquery_to_gcs import (
    BigQueryToGCSOperator,
)
from airflow.utils.state import DagRunState

from dags.storage.models.osint import PackageToVersion
from test_utils.mocks import mock_gcs_connection

pytestmark = pytest.mark.skip


@pytest.fixture()
def dag(dagbag):
    d: DAG = dagbag.get_dag(dag_id="import_package_to_version")
    assert d is not None
    assert len(d.tasks) > 0
    return d


def count_package_to_version(session):
    return session.query(PackageToVersion).count()


def test_dag_happy_case(dag, session):
    assert count_package_to_version(session) == 0
    file_path = "tests/integrations/test_data/scorecard/package_to_version.csv.gz"
    with (
        mock_gcs_connection(download_file_content=file_path),
        patch(
            "dags.google_cloud.import_base._file_name_for_object",
            return_value=file_path,
        ),
        patch.object(BigQueryToGCSOperator, "execute", return_value=None),
        patch.object(BigQueryCreateEmptyDatasetOperator, "execute", return_value=None),
        patch.object(BigQueryInsertJobOperator, "execute", return_value=None),
        patch.object(BigQueryDeleteTableOperator, "execute", return_value=None),
        patch.object(
            GCSListObjectsOperator,
            "execute",
            return_value=["package_to_version.csv.gz"],
        ),
    ):
        dag.test()

    dag_run: DagRun = dag.get_last_dagrun()
    assert dag_run.state == DagRunState.SUCCESS

    assert count_package_to_version(session) > 0
