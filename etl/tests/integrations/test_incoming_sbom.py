import json

import pytest
from airflow import DAG
from airflow.models import DagRun
from airflow.utils.state import DagRunState, State

import dags.base.sbom as sbom_module
from dags.domain.attestations import EvidenceState, ContentType, SignatureStatus
from dags.storage.models.osint import (
    Vulnerability,
    VulAdvisory,
    Attestation,
    Component,
    AttestationComponent,
)
from test_utils.mocks import mock_download_from_s3, mock_grype


@pytest.fixture()
def new_attestation(session, pipeline_run):
    at = Attestation(
        key="s3://foo/test",
        contentType=ContentType.CYCLONEDX,
        contextType="local",
        targetType="image",
        targetName="test",
        context={"name": "test"},
        state=EvidenceState.UPLOADED,
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
    d: DAG = dagbag.get_dag(dag_id="incoming_sbom")
    assert d is not None
    assert len(d.tasks) > 0
    return d


def assert_not_validated_attestations_number(session, num: int):
    assert session.query(Attestation).filter(Attestation.state == EvidenceState.UPLOADED).count() == num


def test_dag_no_attestation(dag):
    with mock_download_from_s3(content_file="tests/integrations/test_data/sbom.json") as mocked_s3, mock_grype(
        content_file="tests/integrations/test_data/sbom.grype.json"
    ) as mocked_grype:
        dag.test()
    assert not mocked_grype.called
    assert not mocked_s3.called
    dag_run: DagRun = dag.get_last_dagrun()
    assert dag_run.state == DagRunState.SUCCESS
    tis = dag_run.get_task_instances()
    assert all(ti.state == State.SKIPPED for ti in tis if ti.task_id != "check_failed")


def test_dag_happy_case(dag, new_attestation, session):
    with mock_download_from_s3(content_file="tests/integrations/test_data/sbom.json") as mocked_s3, mock_grype(
        content_file="tests/integrations/test_data/sbom.grype.json"
    ) as mocked_grype:
        dag.test()
    assert mocked_s3.call_count == 1
    assert mocked_grype.call_count == 1

    dag_run: DagRun = dag.get_last_dagrun()
    assert dag_run.state == DagRunState.SUCCESS

    tis = dag_run.get_task_instances()
    mark_failed_task_id = "check_failed"
    mark_failed = next((ti for ti in tis if ti.task_id == mark_failed_task_id), None)
    assert mark_failed is not None
    assert mark_failed.state == State.SUCCESS  # mark_failed
    assert all(ti.state == State.SUCCESS for ti in tis if ti.task_id != mark_failed_task_id)  # except mark_failed
    session.refresh(new_attestation)
    assert new_attestation.sigStatus == SignatureStatus.UNSIGNED


def test__extract_and_save_dependencies(session, new_attestation):
    session.execute(Component.__table__.delete())
    session.commit()

    sbom_module.extract_and_save_dependencies.function(
        att={
            "key": new_attestation.key,
            "id": new_attestation.id,
        },
        downloaded_attest_path="tests/integrations/test_data/sbom.json",
    )

    new_component_count = session.query(Component).count()
    with open("tests/integrations/test_data/sbom.json") as f:
        data = json.load(f)
    # all except one, because it's not supported
    assert new_component_count == (len(data["components"]) - 1)


def test__run_grype_and_save_deps(session, new_attestation):
    session.execute(VulAdvisory.__table__.delete())
    session.execute(Vulnerability.__table__.delete())
    session.commit()

    with mock_grype(content_file="tests/integrations/test_data/sbom.grype.json") as mocked_grype:
        sbom_module.run_grype_and_save_deps.function(
            att={
                "key": new_attestation.key,
                "id": new_attestation.id,
            },
            downloaded_attest_path="tests/integrations/test_data/sbom.json",
        )
    assert mocked_grype.call_count == 1

    vulns_count = session.query(Vulnerability).count()
    assert vulns_count > 0
