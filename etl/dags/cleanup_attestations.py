from datetime import datetime, timedelta
from airflow import DAG
from airflow.decorators import task, task_group
from airflow.exceptions import AirflowFailException

from dags.base import attestations as base_attestations
from dags.domain.attestations import ContentType
from dags.tools import notify_slack
from dags.tools.airflow import schedule_only_for_cloud


@task(task_id="validate_state")
def validate_state(att: base_attestations.AttestationResultDict) -> None:
    if att["sigStatus"] == base_attestations.SignatureStatus.IN_PROGRESS:
        return
    raise AirflowFailException("Cleanup should not be run on in-progress attestations")


@task_group()
def process_attestation(att: base_attestations.AttestationResultDict):
    validate_state(att) >> base_attestations.mark_done.override()(att, base_attestations.SignatureStatus.UNSIGNED.value)


# TODO: make a dynamic validation of all types that are not processed by other DAGs.
types = [
    ContentType.CYCLONEDX_STATEMENT,
    ContentType.SLSA_STATEMENT,
    ContentType.SSDF,
    ContentType.POLICY_RUN,
    ContentType.SCORECARD,
    ContentType.SLSA_ATTEST,
]

with DAG(
    dag_id="cleanup_attestations",
    schedule=schedule_only_for_cloud(timedelta(minutes=1)),
    start_date=datetime(2023, 3, 20),
    description="Cleanup attestations that are in progress and not processed by any other dag",
    max_active_runs=1,
    catchup=False,
    is_paused_upon_creation=False,
    default_args={
        "on_failure_callback": notify_slack.notify_failure,
    },
):
    process_attestation.expand(
        att=base_attestations.get_new_attestations(
            content_types=[t.value for t in types],
            context_types=None,
        )
    )
