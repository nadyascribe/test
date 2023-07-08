import pendulum
import logging
from pathlib import Path
from sqlalchemy import select
import shutil
import os

from airflow.decorators import dag, task, task_group
from airflow.exceptions import AirflowSkipException
from airflow.utils.trigger_rule import TriggerRule

from dags.storage.queries.users import get_client_id_by_team_id
from dags.tools import common, api, regscan, notify_slack
from dags.storage import get_engine
from dags.domain.regscan import RegistryImageState
from dags.storage.models.osint import RegistryImage

logger = logging.getLogger("airflow.task")


def gen_tmp_path() -> str:
    p = Path("/tmp") / str(common.get_dag_run_timestamp())
    p.mkdir(exist_ok=True, parents=True)
    return str(p)


def on_process_image_failure(context):
    regimg_id = context["task"].op_args[0]
    regscan.set_registry_image_state(regimg_id, RegistryImageState.FAILED)
    notify_slack.notify_failure(context)


@task
def list_registry_images(params=None) -> list:
    states = [RegistryImageState.UNPROCESSED]
    if params["include_failed"]:
        states.append(RegistryImageState.FAILED)
    q = select(RegistryImage).where(RegistryImage.state.in_(states))
    if not params["include_base_images"]:
        q = q.where(RegistryImage.is_base_image.is_distinct_from(True))
    rows = get_engine().execute(q).all()

    regimg_ids = []
    for r in rows:
        for c in ["architecture", "os", "variant"]:
            if params[c] and r.config[c] != params[c]:
                break
        else:
            regimg_ids.append(r.id)

    if not regimg_ids:
        raise AirflowSkipException("No unprocessed images found")
    else:
        return regimg_ids


@task(retries=3, max_active_tis_per_dag=14)
def download_image(regimg_id: int) -> str:
    image = regscan.get_registry_image(regimg_id)
    request_config = regscan.get_request_config(image)
    pull_url = api.get_pull_url(request_config)
    image_url = f"{pull_url}/{image['repository']}@{image['digest']}"
    tmp_path = gen_tmp_path()
    image_tar = f"{tmp_path}/{regimg_id}.tar"
    token = api.get_repository_token(request_config, image["repository"])
    cmd = [
        "skopeo",
        "copy",
        "--src-registry-token",
        token,
        f"docker://{image_url}",
        f"docker-archive://{image_tar}",
        "--retry-times",
        "3",
        "--debug",
    ]
    common.run_subprocess(cmd)
    return image_tar


@task(retries=0, on_failure_callback=on_process_image_failure)
def generate_sbom(regimg_id: int, params=None):
    image = regscan.get_registry_image(regimg_id)
    tmp_path = gen_tmp_path()
    image_tar = f"{tmp_path}/{regimg_id}.tar"
    client_id = params["client_id"] or get_client_id_by_team_id(image["teamId"])
    client_secret = params["client_secret"] or api.get_client_secret(client_id)
    auth0_domain = params["auth0_domain"] or os.environ.get("AUTH0_DOMAIN")
    auth0_scribe_service_audience = params["auth0_scribe_service_audience"] or os.environ.get(
        "AUTH0_SCRIBE_SERVICE_AUDIENCE"
    )
    scribe_api_base_uri = params["scribe_api_base_uri"] or os.environ.get("SCRIBE_API_BASE_URI")
    cmd = [
        f"/opt/valint/valint",
        "bom",
        f"docker-archive:{image_tar}",
        "-E",
        "-f",
        "-v",
        "--scribe.login-url",
        f"https://{auth0_domain}",
        "--scribe.auth.audience",
        auth0_scribe_service_audience,
        "--scribe.url",
        f"{scribe_api_base_uri}/",
        "--product-key",
        image["repository"],
        "--scribe.client-id",
        client_id,
        "--scribe.client-secret",
        client_secret,
    ]
    env = {
        "REGISTRY_PROVIDER": image["provider"],
        "REGISTRY_URL": image["registry_url"],
        "IMAGE_ID": image["image_id"],
        "IMAGE_DIGEST": image["digest"],
        "IMAGE_REPOSITORY": image["repository"],
        "IMAGE_TAG": image["tag"],
        "IMAGE_CREATED": image["config"]["created"],
    }
    for e in env:
        cmd.extend(["-e", e])
    common.run_subprocess(cmd, env)
    Path(image_tar).unlink()


@task
def mark_in_progess(regimg_id: int):
    regscan.set_registry_image_state(regimg_id, RegistryImageState.IN_PROGRESS)


@task(trigger_rule=TriggerRule.ALL_SUCCESS)
def mark_processed(regimg_id: int):
    regscan.set_registry_image_state(regimg_id, RegistryImageState.PROCESSED)


@task(trigger_rule=TriggerRule.ALL_DONE)
def teardown():
    path = gen_tmp_path()
    shutil.rmtree(path)
    logger.info("removed directory tree at path: %s", path)


@task_group
def process_image(regimg_id: int):
    image_tar = download_image(regimg_id)
    image_sbom = generate_sbom(regimg_id)
    mark_in_progess(regimg_id) >> image_tar >> image_sbom >> mark_processed(regimg_id)


@dag(
    "process_images",
    schedule=None,
    catchup=False,
    start_date=pendulum.datetime(2023, 1, 1, tz="UTC"),
    params={
        "include_failed": False,
        "include_base_images": False,
        "repository": None,
        "architecture": None,
        "os": None,
        "variant": None,
        "client_id": None,
        "client_secret": None,
        "auth0_domain": None,
        "auth0_scribe_service_audience": None,
        "scribe_api_base_uri": None,
    },
    is_paused_upon_creation=False,
    default_args={
        "on_failure_callback": notify_slack.notify_failure,
    },
)
def process_images():
    regimg_ids = list_registry_images()

    regimg_ids >> process_image.expand(regimg_id=regimg_ids) >> teardown()


process_images()
