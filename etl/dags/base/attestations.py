import logging
import typing
from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.decorators import task_group
from airflow.exceptions import AirflowSkipException
from airflow.models import Variable, DagRun, TaskInstance, RenderedTaskInstanceFields
from airflow.models.abstractoperator import TaskStateChangeCallback
from airflow.operators.python import task
from airflow.utils.state import TaskInstanceState
from airflow.utils.trigger_rule import TriggerRule

from dags import storage
from dags.domain.attestations import ContentType, SignatureStatus, ContextType
from dags.storage.queries import attestations as db_attestation
from dags.tools import attestation, fs, common
from dags.tools.airflow import schedule_only_for_cloud

logger = logging.getLogger("airflow.task")


class AttestationResultDict(typing.TypedDict):
    id: str
    key: str
    content_type: ContentType
    sigStatus: SignatureStatus
    targetName: str


TaskType = typing.Callable[[AttestationResultDict, str], None]


@task(retries=0)
def download_attestation(att, **kwargs):
    job_id = common.make_job_id()

    db_attestation.set_attestation_job_id(att["id"], job_id)

    return attestation.download(
        key=att["key"],
        target_directory=str(Path(Variable.get("shared_directory")) / job_id),
    )


@task
def mark_done(att, result_state):
    return db_attestation.change_attestation_sigstatus_by_key(
        att["key"],
        result_state,
    )


@task
def teardown(downloaded_attest_path):
    return fs.remove_file(downloaded_attest_path)


def _make_group(
    tasks: list[TaskType] = None,
    tasks_callable: typing.Callable[[AttestationResultDict, str], list[TaskType]] = None,
    result_state: SignatureStatus = SignatureStatus.VERIFIED,
):
    @task_group()
    def process_attestation(attestation_object: AttestationResultDict):
        download_task = download_attestation.override()(att=attestation_object)
        mark_done_task = mark_done.override()(att=attestation_object, result_state=result_state.value)
        teardown_task = teardown.override()(downloaded_attest_path=download_task)
        if tasks is not None:
            processors = [t(att=attestation_object, downloaded_attest_path=download_task) for t in tasks]
        elif tasks_callable is not None:
            processors = tasks_callable(att=attestation_object, downloaded_attest_path=download_task)
        else:
            raise ValueError("Either tasks or tasks_callable should be provided")

        processors >> teardown_task
        teardown_task >> mark_done_task

    return process_attestation


@task()
def get_new_attestations(
    content_types: list[str],
    context_types: list[str] | None,
    dag_run: DagRun | None = None,
) -> list[AttestationResultDict]:
    assert dag_run is not None

    engine = storage.get_engine()
    res: list[AttestationResultDict] = []
    cursor = engine.execute(
        db_attestation.get_new_attestation_for_processing(
            content_types=content_types,
            context_types=context_types,
            att_id=dag_run.conf.get("att_id"),
        )
    )
    for row in cursor:
        res.append(
            AttestationResultDict(
                id=row.id,
                key=row.key,
                content_type=row.contentType,
                targetName=row.targetName,
                sigStatus=row.sigStatus,
            )
        )
    if not res:
        raise AirflowSkipException("No new attestations found")
    return res


@task(trigger_rule=TriggerRule.ALL_DONE)
def check_failed(dag_run: DagRun | None = None):
    assert dag_run
    tis: list[TaskInstance] = dag_run.get_task_instances(state=TaskInstanceState.FAILED)
    logger.info("Failed tasks: %s", tis)
    failed_attestation_ids: set[int] = set()
    for ti in tis:
        data = RenderedTaskInstanceFields.get_templated_fields(ti)
        id_ = data.get("op_kwargs", {}).get("att", {}).get("id")
        if id_ is not None:
            failed_attestation_ids.add(id_)
    logger.info("Failed attestation ids: %s", failed_attestation_ids)
    db_attestation.change_attestation_state_by_ids(list(failed_attestation_ids), SignatureStatus.UNVERIFIED)


# TODO(anton): configure concurrency and schedule per env
def make_dag(
    dag_id: str,
    *,
    content_types: list[ContentType],
    start_date: datetime,
    context_types: list[ContextType] | None = None,
    object_tasks: list[TaskType] = None,
    object_tasks_callable: typing.Callable[[AttestationResultDict, str], list[typing.Any]] = None,
    description: str | None = None,
    result_state: SignatureStatus = SignatureStatus.VERIFIED,
    is_paused_upon_creation: bool = True,
    on_failure_callback: TaskStateChangeCallback | None = None,
    post_group_tasks: list[typing.Callable[[], list[typing.Any]]] | None = None,
):
    if not object_tasks and not object_tasks_callable:
        raise ValueError("Either object_tasks or object_tasks_callable should be provided")
    if object_tasks and object_tasks_callable:
        raise ValueError("Only one of object_tasks or object_tasks_callable should be provided")

    with DAG(
        dag_id=dag_id,
        start_date=start_date,
        schedule=schedule_only_for_cloud(timedelta(minutes=1)),
        description=description,
        max_active_runs=1,
        catchup=False,
        is_paused_upon_creation=is_paused_upon_creation,
        default_args={
            "on_failure_callback": on_failure_callback,
        },
    ) as dag:
        # Receives sboms from database, one row per each DAG run.
        # Will be changed in the future with HTTP-endpoint or something like that.
        get_new_attestations_task = get_new_attestations(
            [c.value for c in content_types],
            [c.value for c in context_types] if context_types is not None else None,
        )

        group = _make_group(tasks=object_tasks, tasks_callable=object_tasks_callable, result_state=result_state).expand(
            attestation_object=get_new_attestations_task
        )
        group >> check_failed()
    return dag
