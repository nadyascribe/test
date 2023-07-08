import logging
from airflow.hooks.base import BaseHook
from github import Github
from github.GithubIntegration import GithubIntegration

from dags.tools import env


logger = logging.getLogger("airflow.task")


def get_conn_id():
    if env.tests_or_local():
        return "github_local"
    return "github_default"


class GithubCredentials:
    def __init__(self, integration_id: str, private_key: str):
        self.integration_id = integration_id
        self.private_key = private_key


def _get_credentials(conn_id: str | None = None) -> GithubCredentials:
    """
    Returns Github credentials from Airflow connection.
    :param conn_id:
    :return:
    """
    conn = BaseHook.get_connection(conn_id or get_conn_id())
    return GithubCredentials(
        integration_id=conn.login,
        private_key=conn.password,
    )


def get_installation_access_token(installation_id: int, repo_id: int) -> str:
    """
    Receives installation access token for specified installation and repo.
    :param installation_id:
    :param repo_id:
    :return:
    """
    creds = _get_credentials()
    auth = GithubIntegration(creds.integration_id, creds.private_key).get_access_token(
        installation_id, _get_permissions([repo_id])
    )
    return auth.token


def get_provenance_artifact_url(token: str, run_id: int, url: str) -> str | None:
    """
    Returns provenance artifact url for specified workflow run id and repo url.
    :param token:
    :param run_id:
    :param url:
    :return:
    """
    artifacts = Github(token).get_repo(url).get_workflow_run(run_id).get_artifacts()
    logger.info(f"artifacts count: {artifacts.totalCount}")
    if artifacts.totalCount == 0:
        return None

    for art in artifacts.get_page(0):
        logger.debug("artifact: %s", art.name)
        if art.name == "provenance":
            return art.archive_download_url
    return None


def _get_permissions(repo_ids: list[int]) -> dict:
    return {
        # "repository_ids": repo_ids,
        # "permissions": {
        "actions": "read",
        "administration": "read",
        "contents": "read",
        "deployments": "read",
        "metadata": "read",
        "members": "read",
        "organization_hooks": "read",
        "packages": "read",
        "pull_requests": "read",
        "repository_hooks": "read",
        # },
    }
