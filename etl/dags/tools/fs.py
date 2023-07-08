import logging
import os.path
import shutil
import uuid
from pathlib import Path

from airflow.models import Variable

from dags.tools import env

logger = logging.getLogger(__name__)


def change_extension(path: str, new_extension: str) -> str:
    """
    Changes extension of specified path to new extension.
    :param path:
    :param new_extension:
    :return:
    """
    return f"{os.path.splitext(path)[0]}.{new_extension}"


def remove_file(path: str) -> None:
    """
    Removes specified file from filesystem. Performs some logging.
    Removal is skipped if environment is local or tests.
    :param path:
    :return:
    """

    logger.debug("clearing path: %s", path)
    if not os.path.exists(path):
        logger.warning("path does not exist: %s", path)
        return

    if not need_cleanup():
        logger.info("skipping removal of path: %s", path)
        return

    os.remove(path)
    logger.info("removed path: %s", path)


def remove_dir_tree(path: str) -> None:
    """
    Removes specified directory tree from filesystem. Performs some logging.
    Removal is skipped if environment is local or tests.
    :param path:
    :return:
    """

    logger.debug("clearing directory tree at path: %s", path)
    if not os.path.exists(path):
        logger.warning("path does not exist: %s", path)
        return

    if not need_cleanup():
        logger.info("skipping removal of path: %s", path)
        return

    shutil.rmtree(path)
    logger.info("removed directory tree at path: %s", path)


def ensure_directory_for_filepath(filepath: str) -> None:
    """
    Ensures that directory for specified filepath exists.
    :param filepath:
    :return:
    """
    Path(filepath).parent.mkdir(exist_ok=True, parents=True)


def need_cleanup() -> bool:
    """
    Returns True if cleanup is needed, False otherwise.
    :return:
    """
    without = env.without_cleanup()
    if without is not None:
        return not without
    return not env.tests_or_local()


def get_tmp_file_path() -> str:
    """
    Generates path to temporary file.
    :return:
    """
    return os.path.join(Variable.get("tmp_directory", "/tmp"), str(uuid.uuid4()))
