import datetime
import os.path
import random
import uuid
from unittest.mock import patch

import pytest
from airflow.decorators import task
from airflow.exceptions import AirflowSkipException
from airflow.models import RenderedTaskInstanceFields

from dags.base import attestations as att_module
from dags.domain.attestations import ContentType, EvidenceState, SignatureStatus
from dags.storage.models.osint import Attestation
from test_utils.mocks import mock_download_from_s3


@pytest.fixture(scope="module")
def content_type():
    return random.choice(list(ContentType))


@pytest.fixture()
def new_attestation(session, content_type, pipeline_run):
    at = Attestation(
        key="s3://foo/test",
        contentType=content_type,
        contextType="local",
        state=EvidenceState.UPLOADED,
        targetType="image",
        targetName="test",
        context={"name": "test"},
        pipelineRun=pipeline_run.id,
    )
    session.add(at)
    session.commit()
    yield at
    session.delete(at)
    session.commit()


@pytest.fixture(scope="module")
def dag(content_type):
    @task()
    def dummy(*a, **kw):
        return None

    return att_module.make_dag(
        "test", description="", object_tasks=[dummy], content_types=[content_type], start_date=datetime.datetime.now()
    )


def assert_not_validated_attestations_number(session, num: int, state: SignatureStatus | None = None):
    q = session.query(Attestation)
    if state is None:
        q = q.filter(Attestation.sigStatus.is_(None))
    else:
        q = q.filter(Attestation.sigStatus == state)

    assert q.count() == num


class DummyDagRun:
    conf = {}


def test__get_new_attestation__no_new_sboms(dag, session, content_type):
    assert_not_validated_attestations_number(session, 0)
    with pytest.raises(AirflowSkipException):
        att_module.get_new_attestations.function(content_types=[content_type], context_types=[], dag_run=DummyDagRun())


def test__get_new_attestation__sbom_exists(dag, session, new_attestation, content_type):
    assert_not_validated_attestations_number(session, 1)
    res = att_module.get_new_attestations.function(
        content_types=[content_type], context_types=[], dag_run=DummyDagRun()
    )

    assert len(res) == 1
    res = res[0]

    assert res["id"] == new_attestation.id
    assert res["key"] == new_attestation.key


def test__download_attestation(dag, tmp_dir):
    download_path = f"{tmp_dir}/foo/bar/baz.json"

    class MockAirflowObj:
        id = str(uuid.uuid4())
        map_index = 1

    with mock_download_from_s3(content_file=download_path) as mocked_s3:
        res = att_module.download_attestation.function(
            att={
                "key": "s3://foo/test",
                "id": 1,
            },
            dag_run=MockAirflowObj(),
            ti=MockAirflowObj(),
        )
    assert mocked_s3.call_count == 1

    assert res is not None
    assert res == download_path


@pytest.mark.parametrize("result_state", [SignatureStatus.VERIFIED, SignatureStatus.UNVERIFIED])
def test__mark_done(dag, session, new_attestation, result_state):
    assert_not_validated_attestations_number(session, 0, state=result_state)

    att_module.mark_done.function(
        att={
            "key": "s3://foo/test",
            "id": 1,
        },
        result_state=result_state,
    )
    assert_not_validated_attestations_number(session, 1, state=result_state)


def test__mark_failed(dag, session, new_attestation):
    assert_not_validated_attestations_number(session, 1)

    class DagRunStub:
        def get_task_instances(self, *args, **kwargs):
            return [1]

    with patch.object(
        RenderedTaskInstanceFields,
        "get_templated_fields",
        return_value={"op_kwargs": {"att": {"id": new_attestation.id}}},
    ):
        att_module.check_failed.function(
            dag_run=DagRunStub(),
        )
    assert_not_validated_attestations_number(session, 1, state=SignatureStatus.UNVERIFIED)


def test__teardown__enabled(dag, session):
    # create file
    file_path = f"/tmp/{uuid.uuid4()}"
    with open(file_path, "w"):
        pass

    with patch("dags.tools.fs.need_cleanup", return_value=False):
        att_module.teardown.function(file_path)
    assert os.path.exists(file_path)

    with patch("dags.tools.fs.need_cleanup", return_value=True):
        att_module.teardown.function(file_path)
    assert not os.path.exists(file_path)
