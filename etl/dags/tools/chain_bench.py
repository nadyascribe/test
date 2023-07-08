import json
import logging
import re
from typing import Any

from airflow.exceptions import AirflowFailException
from airflow.hooks.subprocess import SubprocessHook
from airflow.models import Variable

from dags.tools import fs

logger = logging.getLogger("airflow.task")


class ChainBenchException(Exception):
    pass


def run(*, repo_url: str, access_token: str) -> dict[str, Any]:
    """
    Runs chainbench binary and returns sarif results.
    :param repo_url:
    :param access_token:
    :return:
    """
    cb_path = Variable.get("chainbench_bin_path")

    out_file = fs.get_tmp_file_path()

    result = _call_subprocess(cb_path, out_file, repo_url, access_token)
    if result.exit_code != 0:
        logger.error("chainbench failed with exit_code: %s", result.exit_code)
        raise AirflowFailException("chainbench failed")

    sarif_result = convert_file_to_sarif(out_file)
    fs.remove_file(out_file)
    return sarif_result


_re_links = re.compile("(https?:\/\/\S+)")


def convert_file_to_sarif(file_path: str) -> dict[str, Any]:
    """
    Converts chainbench results (file content) to sarif format.
    :param file_path:
    :return:
    """
    with open(file_path) as f:
        results = json.load(f)
    return convert_object_to_sarif(results)


def convert_object_to_sarif(cis_results: dict[str, Any]):
    """
    Converts chainbench results (object) to sarif format.
    :param cis_results:
    :return:
    """
    sarif_results = []
    rules = []
    for result in cis_results["results"]:
        check_res = result["result"]
        if check_res == "Failed":
            level = "error"
            res = "fail"
        elif check_res == "Passed":
            level = "note"
            res = "pass"
        elif check_res == "Unknown":
            level = "warning"
            res = "review"
        else:
            raise ChainBenchException(f"Unknown result type: {check_res}")
        text = {"text": _re_links.sub('<a href="$1" target="_blank">here</a>', result["remediation"])}

        messages = {
            "fail": text,
            "pass": text,
            "review": text,
        }

        if res not in messages:
            raise ChainBenchException(f"Unknown result type: {res}")

        sarif_results.append(
            {
                "level": level,
                "ruleId": result["id"],
                "message": {
                    "id": res,
                },
            }
        )
        rules.append(
            {
                "fullDescription": {
                    "text": result["description"],
                },
                "messageStrings": messages,
                "name": result["name"],
                "id": result["id"],
                "shortDescription": {
                    "text": result["name"],
                },
            }
        )
    return {
        "$schema": "https://schemastore.azurewebsites.net/schemas/json/sarif-2.1.0-rtm.4.json",
        "version": "2.1.0",
        "runs": [
            {
                "results": sarif_results,
                "tool": {
                    "driver": {
                        "name": "Chain Bench",
                        "rules": rules,
                    }
                },
            }
        ],
    }


def _call_subprocess(cb_path: str, out_file: str, repo_url: str, access_token: str):
    return SubprocessHook().run_command(
        [
            cb_path,
            "scan",
            "--repository-url",
            repo_url,
            "--access-token",
            access_token,
            "-o",
            out_file,
            "-vv",
        ]
    )
