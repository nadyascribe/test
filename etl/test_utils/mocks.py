import os.path
import uuid
from contextlib import contextmanager
from typing import Optional
from unittest.mock import patch, PropertyMock, MagicMock

from airflow.providers.google.cloud.hooks.gcs import GCSHook


@contextmanager
def mock_download_from_s3(
    content_file: Optional[str] = None,
    content: Optional[str] = None,
    side_effect: Optional[Exception] = None,
):
    content_file = _content_or_file(content=content, content_file=content_file)
    with patch(
        "dags.tools.s3.download_from_s3",
        return_value=content_file,
        side_effect=side_effect,
    ) as mocked:
        yield mocked


@contextmanager
def mock_grype(
    content_file: Optional[str] = None,
    content: Optional[str] = None,
    side_effect: Optional[Exception] = None,
):
    content_file = _content_or_file(content=content, content_file=content_file)
    with patch("dags.tools.grype.run", return_value=content_file, side_effect=side_effect) as mocked:
        yield mocked


@contextmanager
def mock_sig_verifier_cmd(side_effect: Optional[Exception] = None):
    with patch("dags.tools.sig_verifier.run", side_effect=side_effect) as mocked:
        yield mocked


def _content_or_file(content_file: Optional[str] = None, content: Optional[str] = None) -> Optional[str]:
    if not content_file and not content:
        return None
    if content_file and content:
        raise ValueError("Cannot specify both content and content_file")
    if content:
        content_file = f"tests/integrations/test_data/tmp/{uuid.uuid4()}.json"
        if not os.path.exists(os.path.dirname(content_file)):
            os.makedirs(os.path.dirname(content_file))
        with open(content_file, "w") as f:
            f.write(content)
    return content_file


@contextmanager
def mock_gcs_connection(download_file: Optional[str] = None, download_file_content: Optional[str] = None):
    download_file = _content_or_file(content=download_file_content, content_file=download_file)
    with patch.multiple(
        GCSHook,
        download=MagicMock(return_value=download_file),
        get_conn=MagicMock(),
        project_id=PropertyMock(return_value="gc_fooo"),
    ) as mocked:
        yield mocked


@contextmanager
def mock_get_tmp_file_path(path):
    with patch("dags.tools.fs.get_tmp_file_path", return_value=path) as p:
        yield p
