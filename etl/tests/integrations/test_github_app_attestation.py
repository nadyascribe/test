from contextlib import contextmanager
from unittest.mock import patch

import pytest
from airflow import DAG
from airflow.models import DagRun
from airflow.utils.state import DagRunState, State

from dags.storage.models import osint


@pytest.fixture(scope="module")
def dag(dagbag):
    d: DAG = dagbag.get_dag(dag_id="github-app-attestations")
    assert d is not None
    assert len(d.tasks) > 0
    return d


@contextmanager
def mock_chain_bench(result_report):
    with patch("dags.tools.chain_bench.run", return_value=result_report) as mocked:
        yield mocked


@contextmanager
def mock_opa(result_report):
    with patch("dags.tools.opa.run", return_value=result_report) as mocked:
        yield mocked


@contextmanager
def mock_get_token():
    with patch("dags.tools.github.get_installation_access_token", return_value="gh_token") as mocked:
        yield mocked


@contextmanager
def mock_get_provenance():
    with patch("dags.tools.github.get_provenance_artifact_url", return_value="gh_token") as mocked:
        yield mocked


@pytest.fixture()
def default_sarif_report():
    return {"runs": [{"results": [{"ruleId": "GGS001", "message": {"id": "pass"}}]}]}


def test_dag_happy_case(dag, session, default_sarif_report, pipeline_run):
    with (
        mock_get_token() as mocked_get_token,
        mock_get_provenance() as mocked_get_provenance,
        mock_opa(default_sarif_report) as mocked_opa,
        mock_chain_bench(default_sarif_report) as mocked_cb,
    ):
        dag.test(
            run_conf={
                "installation_id": 1,
                "repository_id": 1,
                "pipeline_run_id": pipeline_run.id,
                "repository_url": "foo",
                "build_script_path": "foo",
                "default_branch": "foo",
                "repo_full_name": "foo",
                "workflow_run_id": 1,
            }
        )
    assert mocked_get_token.call_count == 1
    assert mocked_opa.call_count == 1
    assert mocked_cb.call_count == 1
    assert mocked_get_provenance.call_count == 1

    dag_run: DagRun = dag.get_last_dagrun()
    assert dag_run.state == DagRunState.SUCCESS

    tis = dag_run.get_task_instances()
    assert all(ti.state == State.SUCCESS for ti in tis)  # except mark_failed
    # one complianceRun by each tool
    assert session.query(osint.ComplianceRun).count() == 2
