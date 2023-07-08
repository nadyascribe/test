import os

from dags.tools.funcs import str_to_int, str_to_bool


def environment() -> str | None:
    """
    :return: local, tests, local-docker or any other specified
    :return:
    """
    return os.getenv("ENVIRONMENT")


def is_local(env: str | None = None):
    return (env or environment()) == "local"


def is_tests(env: str | None = None):
    return (env or environment()) == "tests"


def is_local_docker(env: str | None = None):
    return (env or environment()) == "local-docker"


def is_not_cloud():
    """
    Returns True if running on local, local-docker or tests
    :return:
    """
    return is_local() or is_local_docker() or is_tests()


def tests_or_local():
    return is_tests() or is_local()


def without_cleanup() -> bool | None:
    """
    :return: True if WITHOUT_CLEANUP is set to true
    """
    if "WITHOUT_CLEANUP" not in os.environ:
        return None
    return str_to_bool(os.environ["WITHOUT_CLEANUP"])


def cloud_imports_limit() -> int | None:
    """
    :return: CLOUD_IMPORTS_LIMIT if set, None otherwise
    """
    if "CLOUD_IMPORTS_LIMIT" not in os.environ:
        return None
    return str_to_int(os.environ["CLOUD_IMPORTS_LIMIT"])


def no_scheduler_dags() -> bool:
    """
    :return: True if NO_SCHEDULED_DAGS is set to true
    """
    return str_to_bool(os.environ.get("NO_SCHEDULED_DAGS"))
