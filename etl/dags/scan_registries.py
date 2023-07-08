import pendulum
import logging
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

from airflow.decorators import dag, task

from dags.storage import get_engine
from dags.storage.models.osint import RegistryScanConfig, RegistryImage
from dags.tools import api, regscan, notify_slack


logger = logging.getLogger("airflow.task")


@task
def list_registry_configs(params=None) -> list[dict]:
    q = select(RegistryScanConfig)
    if params["team_ids"]:
        q = q.where(RegistryImage.teamId.in_(params["team_ids"]))
    if params["providers"]:
        q = q.where(RegistryImage.provider.in_(params["providers"]))
    rows = get_engine().execute(q).all()
    return [values._asdict() for values in rows]


@task
def insert_registry_images(config: dict, params=None) -> list[dict]:
    request_config = regscan.get_request_config(config, params["config"])
    images = api.scan_registry(request_config, params["is_base_image"])
    rows = get_engine().execute(
        insert(RegistryImage).on_conflict_do_nothing().returning(RegistryImage.id),
        images,
    )
    return [r.id for r in rows]


@dag(
    "scan_registries",
    schedule=None,
    catchup=False,
    start_date=pendulum.datetime(2023, 1, 1, tz="UTC"),
    params={
        "team_ids": [],
        "providers": [],
        "is_base_image": None,
        "config": {
            "registry_url": None,
            "username": None,
            "password": None,
            "repos_filter": {
                "repositories": [],
                "architectures": [],
                "oss": [],
            },
        },
    },
    is_paused_upon_creation=False,
    default_args={
        "on_failure_callback": notify_slack.notify_failure,
    },
)
def scan_registries():
    configs = list_registry_configs()
    insert_registry_images.expand(config=configs)


scan_registries()
