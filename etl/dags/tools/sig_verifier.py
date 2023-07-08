import logging
from typing import List

from airflow.exceptions import AirflowFailException
from airflow.hooks.subprocess import SubprocessHook, SubprocessResult
from airflow.models import Variable

logger = logging.getLogger("airflow.task")


def run(file_path: str) -> None:
    scribe_service_bin_path = Variable.get("scribe_service_bin_path")
    result = _run_cmd(scribe_service_bin_path, ["sig-verify", file_path])
    if result.exit_code != 0:
        logger.error("sig-verifier failed: %s", result.output)
        raise AirflowFailException("sig-verifier failed")


def _run_cmd(cmd_path: str, cmd_args: List[str]) -> SubprocessResult:
    logger.info('execute "%s %s"', cmd_path, cmd_args)
    return SubprocessHook().run_command(
        [
            cmd_path,
        ]
        + cmd_args
    )
