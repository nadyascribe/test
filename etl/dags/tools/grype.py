import base64
import json
import logging
import os
from pathlib import Path
from typing import List

from airflow.exceptions import AirflowFailException
from airflow.hooks.subprocess import SubprocessHook, SubprocessResult
from airflow.models import Variable
from filelock import FileLock

logger = logging.getLogger("airflow.task")

# better to run it manually with manually-acquiring lock,
# otherwise concurrent database update may happen and grype-db may be corrupted
UPDATE_GRYPE_MANUALLY = True


def run(file_path: str, output: str) -> None:
    """
    Runs grype on specified file and saves result to specified output file.
    Checks grype-db version and updates it if needed.
    :param file_path:
    :param output:
    :return:
    """
    grype_path = Variable.get("grype_path")
    if UPDATE_GRYPE_MANUALLY:
        _check_grype_db(grype_path=grype_path)
    result = _run_grype_cmd(grype_path, [file_path, "-o", "json", "--file", output])
    if result.exit_code != 0:
        logger.error("grype failed with exit_code: %s", result.exit_code)
        raise AirflowFailException("grype failed")


_GRYPE_DATE_FORMAT = "%Y-%m-%d %H:%M:%S %z %Z"


def _run_grype_cmd(grype_path: str, cmd_args: List[str]) -> SubprocessResult:
    logger.info('execute "%s %s"', grype_path, cmd_args)
    params = [
        grype_path,
        "-c",
        str(Path(grype_path).parent / ".grype.yaml"),
    ] + cmd_args
    res = SubprocessHook().run_command(params)
    logger.info("grype output: %s", res.output)
    return res


def _check_grype_db(grype_path: str) -> None:
    lock = FileLock("/tmp/grype-update-db.lock", timeout=120)
    logger.info("acquire lock for grype db update")
    with lock:
        check_result = _run_grype_cmd(grype_path, ["db", "status"])
        if check_result.exit_code == 0:
            logger.info("no need to update grype db: %s", check_result.output)
            return

        update_result = _run_grype_cmd(grype_path, ["db", "update"])
        if update_result.exit_code != 0:
            raise AirflowFailException("grype failed")


def extract_syft(sbom_path: str) -> str:
    """
    Extracts syft from sbom file and saves it to file with same name but .syft extension.
    :param sbom_path:
    :return:
    """
    with open(sbom_path, "rb") as f:
        sbom = json.load(f)

    syft_path = f"{os.path.splitext(sbom_path)[0]}.syft"

    for comp in sbom.get("components") or []:
        if comp["group"] != "syft":
            continue
        for prop in comp.get("properties") or []:
            if prop["name"] != "content":
                continue
            with open(syft_path, "wb") as f:
                f.write(base64.b64decode(prop["value"]))
            return syft_path
    else:
        raise ValueError("syft section not found")
