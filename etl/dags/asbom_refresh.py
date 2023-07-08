import logging
from datetime import timedelta

import pendulum
from airflow import DAG
from airflow.decorators import task
from airflow.utils.helpers import chain

from dags.storage import get_engine
from dags.storage.models.asbom import MAT_VIEWS
from dags.storage.sqla_utils import refresh_view
from dags.tools import notify_slack
from dags.tools.airflow import schedule_only_for_cloud

logger = logging.getLogger("airflow.task")

asbom_refresh = DAG(
    "asbom_refresh",
    schedule=schedule_only_for_cloud(timedelta(hours=3)),
    max_active_runs=1,
    catchup=False,
    start_date=pendulum.datetime(2023, 1, 1),
    is_paused_upon_creation=False,
    default_args={"on_failure_callback": notify_slack.notify_failure},
)


@task
def refresh_view_task(schema_name, view_name):
    """
    Refreshes a view in the database.
    """
    with get_engine().begin() as transaction:
        refresh_view(transaction, schema_name, view_name)


with asbom_refresh:
    ch = []
    for view in MAT_VIEWS:
        task = refresh_view_task(view.schema, view.signature)
        ch.append(task)
    chain(*ch)
