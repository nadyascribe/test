import json
import logging
import os.path
from typing import Any

from airflow.exceptions import AirflowFailException
from airflow.hooks.subprocess import SubprocessHook, SubprocessResult
from airflow.models import Variable

from dags.tools import fs

logger = logging.getLogger("airflow.task")


def run(
    *,
    build_script_path: str,
    protected_branch: str,
    repository_name: str,
    repo_url: str,
    provenance_url: str | None,
    token: str,
) -> dict[str, Any]:
    scribe_service_bin_path = Variable.get("scribe_service_bin_path")

    policy_path = Variable.get("github_posture_policy_path")
    policy_path = os.path.join(policy_path, "github")

    out_file = fs.get_tmp_file_path()

    result = _call_subprocess(
        scribe_service_bin_path,
        out_file,
        policy_path,
        build_script_path,
        protected_branch,
        repository_name,
        repo_url,
        token,
        provenance_url or "",
    )
    if result.exit_code != 0:
        logger.error("opa failed with exit_code: %s", result.exit_code)
        raise AirflowFailException("opa failed")

    with open(out_file) as f:
        sarif_data = json.load(f)
    fs.remove_file(out_file)
    return sarif_data


def _call_subprocess(
    scribe_service_bin_path: str,
    out_file: str,
    policy_path: str,
    build_script_path: str,
    protected_branch: str,
    repository_name: str,
    repo_url: str,
    token: str,
    provenance_url: str,
) -> SubprocessResult:
    """
    separated function for testing purposes
    """
    return SubprocessHook().run_command(
        [
            scribe_service_bin_path,
            "opa",
            "--build-script-path",
            build_script_path,
            "--out",
            out_file,
            "--policy-path",
            policy_path,
            "--protected-branch",
            protected_branch,
            "--provenance-file-url",
            provenance_url,
            "--repository-name",
            repository_name,
            "--repository-url",
            repo_url,
            "--token",
            token,
        ]
    )
