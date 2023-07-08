import pytest
from airflow import DAG
from airflow.models import DagRun
from airflow.utils.state import DagRunState, State

from dags.domain.attestations import EvidenceState, ContentType, SignatureStatus
from dags.storage.models.osint import Attestation, AttestationComponent
from test_utils.mocks import mock_sig_verifier_cmd, mock_download_from_s3, mock_grype


@pytest.fixture()
def new_attestation(session, pipeline_run):
    at = Attestation(
        key="s3://foo/test",
        contentType=ContentType.CYCLONEDX_ATTEST,
        contextType="local",
        targetType="image",
        targetName="test",
        state=EvidenceState.UPLOADED,
        context={"name": "test"},
        pipelineRun=pipeline_run.id,
    )
    session.add(at)
    session.commit()
    yield at
    session.execute(AttestationComponent.__table__.delete())
    session.delete(at)
    session.commit()


@pytest.fixture()
def dag(dagbag):
    d: DAG = dagbag.get_dag(dag_id="signed_sbom")
    assert d is not None
    assert len(d.tasks) > 0
    return d


def test_dag_no_attestation(dag):
    dag.test()
    dag_run: DagRun = dag.get_last_dagrun()
    assert dag_run.state == DagRunState.SUCCESS
    tis = dag_run.get_task_instances()
    assert all(ti.state == State.SKIPPED for ti in tis if ti.task_id != "check_failed")


def test_dag_happy_case(dag, new_attestation, session):
    with (
        mock_sig_verifier_cmd() as mocked_cmd,
        mock_download_from_s3(content_file="tests/integrations/test_data/signed_sbom.json") as mocked_s3,
        mock_grype(content_file="tests/integrations/test_data/sbom.grype.json") as mocked_grype,
    ):
        dag.test()
    assert mocked_s3.call_count == 1
    assert mocked_cmd.call_count == 1
    assert mocked_grype.call_count == 1
    dag_run: DagRun = dag.get_last_dagrun()
    assert dag_run.state == DagRunState.SUCCESS

    tis = dag_run.get_task_instances()
    check_failed_task_id = "check_failed"
    mark_failed = next((ti for ti in tis if ti.task_id == check_failed_task_id), None)
    assert mark_failed is not None
    assert mark_failed.state == State.SUCCESS  # mark_failed
    assert all(ti.state == State.SUCCESS for ti in tis if ti.task_id != check_failed_task_id)  # except mark_failed
    session.refresh(new_attestation)
    assert new_attestation.sigStatus == SignatureStatus.VERIFIED
