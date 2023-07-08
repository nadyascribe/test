import json
import os
from pathlib import Path
from unittest import mock

import pytest
from airflow.exceptions import AirflowFailException
from airflow.hooks.subprocess import SubprocessHook

from dags.tools import opa
from test_utils.mocks import mock_get_tmp_file_path


SLSA_FILE_PATH = "tests/integrations/test_data/slsa.json"


@pytest.fixture()
def mock_vars():
    f = Path("/tmp/foo")
    f.touch()
    with mock.patch.dict(
        os.environ,
        {
            "AIRFLOW_VAR_SCRIBE_SERVICE_BIN_PATH": str(f),
            "AIRFLOW_VAR_GITHUB_POSTURE_POLICY_PATH": str(f),
        },
    ):
        yield
    f.unlink()


@pytest.fixture()
def mock_opa(request):
    class Result:
        exit_code = getattr(request, "param", 0)

    with mock.patch("dags.tools.opa._call_subprocess", return_value=Result()) as m:
        yield m


@pytest.mark.usefixtures("mock_vars")
def test_run(mock_opa):
    with mock_get_tmp_file_path(SLSA_FILE_PATH):
        result = opa.run(
            build_script_path="build_script_path",
            protected_branch="protected_branch",
            repository_name="repository_name",
            repo_url="repo_url",
            token="token",
            provenance_url="http://localhost:7654",
        )
    assert mock_opa.call_count == 1
    with open(SLSA_FILE_PATH) as f:
        expected = json.load(f)
    assert expected == result


@pytest.mark.usefixtures("mock_vars")
@pytest.mark.parametrize("mock_opa", [1], indirect=True)
def test_failed(mock_opa):
    with pytest.raises(AirflowFailException):
        opa.run(
            build_script_path="build_script_path",
            protected_branch="protected_branch",
            repository_name="repository_name",
            repo_url="repo_url",
            token="token",
            provenance_url="http://localhost:7654",
        )
    assert mock_opa.call_count == 1
