import logging
from datetime import datetime

from dags.base import attestations as attestations_base
from dags.base.sbom import make_tasks
from dags.domain.attestations import ContentType, SignatureStatus
from dags.tools import notify_slack

logger = logging.getLogger("airflow.task")


dag = attestations_base.make_dag(
    "incoming_sbom",
    object_tasks_callable=make_tasks,
    content_types=[ContentType.CYCLONEDX],
    start_date=datetime(2023, 3, 20),
    description="Process incoming SBOMs",
    result_state=SignatureStatus.UNSIGNED,
    is_paused_upon_creation=False,
    on_failure_callback=notify_slack.notify_failure,
)
