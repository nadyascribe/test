import logging
from sqlalchemy import select, update

from airflow.exceptions import AirflowFailException

from dags.tools import api, common
from dags.storage import get_engine
from dags.storage.models.osint import RegistryScanConfig, RegistryImage
from dags.domain.regscan import RegistryImageState

logger = logging.getLogger("airflow.task")


def get_registry_image(regimg_id: int) -> dict:
    values = (
        get_engine()
        .execute(
            select(RegistryImage, RegistryScanConfig)
            .where(RegistryImage.id == regimg_id)
            .where(RegistryImage.registry_scan_config == RegistryScanConfig.id)
        )
        .first()
    )
    return values._asdict()


def get_request_config(registry_config: dict, params_config: dict = None) -> dict:
    body = common.merge_dicts(registry_config, params_config)
    body["password"] = api.decrypt(body["password"]) if body["password"] else None
    body["token"] = api.decrypt(body["token"]) if body["token"] else None
    return body


def set_registry_image_state(regimg_id: int, state: RegistryImageState) -> None:
    logger.info(f"Setting state of {regimg_id} to {state}")
    rows = get_engine().execute(
        update(RegistryImage)
        .where(RegistryImage.id == regimg_id)
        .where(RegistryImage.state != state)
        .values(state=state)
        .returning(RegistryImage.id)
    )
    if rows.rowcount != 1:
        logger.error("Failed to update state for regimg_id: %d", regimg_id)
        raise AirflowFailException("Failed to update image state")
