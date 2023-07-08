import os
from pathlib import Path
from unittest import mock

import pytest
from airflow.exceptions import AirflowFailException

from dags.tools import chain_bench
from test_utils.mocks import mock_get_tmp_file_path


CHAIN_BENCH_RESULT_FILE_PATH = "tests/integrations/test_data/chain_bench_report.json"
EXPECTED_CHAIN_BENCH_RESULT = {
    "$schema": "https://schemastore.azurewebsites.net/schemas/json/sarif-2.1.0-rtm.4.json",
    "version": "2.1.0",
    "runs": [
        {
            "results": [
                {"level": "warning", "ruleId": "1.1.3", "message": {"id": "review"}},
                {"level": "error", "ruleId": "1.1.6", "message": {"id": "fail"}},
                {"level": "note", "ruleId": "1.1.4", "message": {"id": "pass"}},
            ],
            "tool": {
                "driver": {
                    "name": "Chain Bench",
                    "rules": [
                        {
                            "fullDescription": {
                                "text": "Ensure that every code change is reviewed and approved by two authorized contributors who are strongly authenticated."
                            },
                            "messageStrings": {
                                "fail": {
                                    "text": 'An organization can protect specific code branches — for example, the "main" branch which often is the version deployed to production — by setting protection rules. These rules secure your code repository from unwanted or unauthorized changes. You may set requirements for any code change to that branch, and thus specify a minimum number of reviewers required to approve a change.'
                                },
                                "pass": {
                                    "text": 'An organization can protect specific code branches — for example, the "main" branch which often is the version deployed to production — by setting protection rules. These rules secure your code repository from unwanted or unauthorized changes. You may set requirements for any code change to that branch, and thus specify a minimum number of reviewers required to approve a change.'
                                },
                                "review": {
                                    "text": 'An organization can protect specific code branches — for example, the "main" branch which often is the version deployed to production — by setting protection rules. These rules secure your code repository from unwanted or unauthorized changes. You may set requirements for any code change to that branch, and thus specify a minimum number of reviewers required to approve a change.'
                                },
                            },
                            "name": "Ensure any change to code receives approval of two strongly authenticated users",
                            "id": "1.1.3",
                            "shortDescription": {
                                "text": "Ensure any change to code receives approval of two strongly authenticated users"
                            },
                        },
                        {
                            "fullDescription": {
                                "text": "Ensure that every code change is reviewed and approved by two authorized contributors who are strongly authenticated."
                            },
                            "messageStrings": {
                                "fail": {
                                    "text": 'An organization can protect specific code branches — for example, the "main" branch which often is the version deployed to production — by setting protection rules. These rules secure your code repository from unwanted or unauthorized changes. You may set requirements for any code change to that branch, and thus specify a minimum number of reviewers required to approve a change.'
                                },
                                "pass": {
                                    "text": 'An organization can protect specific code branches — for example, the "main" branch which often is the version deployed to production — by setting protection rules. These rules secure your code repository from unwanted or unauthorized changes. You may set requirements for any code change to that branch, and thus specify a minimum number of reviewers required to approve a change.'
                                },
                                "review": {
                                    "text": 'An organization can protect specific code branches — for example, the "main" branch which often is the version deployed to production — by setting protection rules. These rules secure your code repository from unwanted or unauthorized changes. You may set requirements for any code change to that branch, and thus specify a minimum number of reviewers required to approve a change.'
                                },
                            },
                            "name": "Ensure any change to code receives approval of two strongly authenticated users",
                            "id": "1.1.6",
                            "shortDescription": {
                                "text": "Ensure any change to code receives approval of two strongly authenticated users"
                            },
                        },
                        {
                            "fullDescription": {
                                "text": "Ensure that every code change is reviewed and approved by two authorized contributors who are strongly authenticated."
                            },
                            "messageStrings": {
                                "fail": {
                                    "text": 'An organization can protect specific code branches — for example, the "main" branch which often is the version deployed to production — by setting protection rules. These rules secure your code repository from unwanted or unauthorized changes. You may set requirements for any code change to that branch, and thus specify a minimum number of reviewers required to approve a change.'
                                },
                                "pass": {
                                    "text": 'An organization can protect specific code branches — for example, the "main" branch which often is the version deployed to production — by setting protection rules. These rules secure your code repository from unwanted or unauthorized changes. You may set requirements for any code change to that branch, and thus specify a minimum number of reviewers required to approve a change.'
                                },
                                "review": {
                                    "text": 'An organization can protect specific code branches — for example, the "main" branch which often is the version deployed to production — by setting protection rules. These rules secure your code repository from unwanted or unauthorized changes. You may set requirements for any code change to that branch, and thus specify a minimum number of reviewers required to approve a change.'
                                },
                            },
                            "name": "Ensure any change to code receives approval of two strongly authenticated users",
                            "id": "1.1.4",
                            "shortDescription": {
                                "text": "Ensure any change to code receives approval of two strongly authenticated users"
                            },
                        },
                    ],
                }
            },
        }
    ],
}


@pytest.fixture()
def mock_vars():
    f = Path("/tmp/foo")
    f.touch()
    with mock.patch.dict(
        os.environ,
        {
            "AIRFLOW_VAR_CHAINBENCH_BIN_PATH": str(f),
        },
    ):
        yield
    f.unlink()


@pytest.fixture()
def mock_chain_bench(request):
    class Result:
        exit_code = getattr(request, "param", 0)

    with mock.patch("dags.tools.chain_bench._call_subprocess", return_value=Result()) as m:
        yield m


@pytest.mark.usefixtures("mock_vars")
def test_run(mock_chain_bench):
    with mock_get_tmp_file_path(CHAIN_BENCH_RESULT_FILE_PATH):
        result = chain_bench.run(
            repo_url="repo_url",
            access_token="token",
        )
    assert mock_chain_bench.call_count == 1
    assert EXPECTED_CHAIN_BENCH_RESULT == result


@pytest.mark.usefixtures("mock_vars")
@pytest.mark.parametrize("mock_chain_bench", [1], indirect=True)
def test_failed(mock_chain_bench):
    with pytest.raises(AirflowFailException):
        chain_bench.run(
            repo_url="repo_url",
            access_token="token",
        )
    assert mock_chain_bench.call_count == 1
