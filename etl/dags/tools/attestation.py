import base64
import json
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from dags.tools.s3 import download_to_directory


def download(key: str, target_directory: str) -> str:
    """
    Downloads attestation (a file) using specified key (URI). If uri schema is s3 than it will be downloaded from s3.
    All other schemas are not supported yet.
    :param key: file's URI
    :param target_directory: directory where file will be downloaded
    :return: result file's path
    """
    parsed = urlsplit(key)
    if parsed.scheme == "s3":
        return download_to_directory(parsed.path[1:], parsed.netloc, target_directory)
    raise ValueError(f'Unsupported scheme: "{parsed.scheme}"')


def extract_cdx_from_signed_sbom(signed_sbom_path: str) -> dict[str, Any]:
    """
    Extracts cdx from signed sbom.
    :param signed_sbom_path:
    :return:
    """
    j = json.loads(Path(signed_sbom_path).read_text())
    a = base64.b64decode(j["payload"])
    b = base64.b64decode(json.loads(a)["payload"])
    return json.loads(b)["predicate"]["bom"]
