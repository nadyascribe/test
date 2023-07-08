import json
import os
import typing
from datetime import datetime

from airflow.decorators import task

from dags.base import attestations as attestations_base
from dags.domain.attestations import ContentType
from dags.base.sbom import make_tasks as make_sbom_tasks
from dags.tools import sig_verifier, notify_slack, fs
from dags.tools.attestation import extract_cdx_from_signed_sbom


@task(task_id="run_verifier")
def run_verifier(downloaded_attest_path: str) -> None:
    """
    Verifies sbom is signed
    :return:
    """
    sig_verifier.run(downloaded_attest_path)


@task(task_id="get_original_sbom")
def get_original_sbom(downloaded_attest_path: str):
    """
    Extracts an original sbom (cyclonedx-json) from signed sbom (attest-cyclonedx-json)
    and store it into the fs.
    """
    dumped = extract_cdx_from_signed_sbom(downloaded_attest_path)
    sbom_path = f"{os.path.splitext(downloaded_attest_path)[0]}-sbom.json"
    with open(sbom_path, "w") as file:
        json.dump(dumped, file)
    return sbom_path


@task(task_id="remove_file")
def remove_file(sbom_path: str):
    fs.remove_file(sbom_path)


def make_tasks(att: attestations_base.AttestationResultDict, downloaded_attest_path: str) -> list[typing.Any]:
    original_sbom_path = get_original_sbom(downloaded_attest_path)
    verify = run_verifier(downloaded_attest_path)
    remove = remove_file(original_sbom_path)
    original_tasks = make_sbom_tasks(att, original_sbom_path)
    verify >> original_sbom_path >> original_tasks >> remove
    return original_tasks + [original_sbom_path, verify, remove]


dag = attestations_base.make_dag(
    "signed_sbom",
    object_tasks_callable=make_tasks,
    description="Process incoming signed (attest-cyclonedx-json) SBOMs: verifies a sign and ingest as a common SBOM",
    content_types=[ContentType.CYCLONEDX_ATTEST],
    start_date=datetime(2023, 3, 20),
    is_paused_upon_creation=False,
    on_failure_callback=notify_slack.notify_failure,
)
