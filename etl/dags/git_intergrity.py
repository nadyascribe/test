import logging
from typing import Literal
from datetime import datetime, timedelta

from airflow.decorators import dag, task, task_group
from airflow.exceptions import AirflowSkipException
from airflow.models import Variable
from sqlalchemy import select, update, cast, String
from sqlalchemy.dialects.postgresql import insert

from dags.storage import get_engine
from dags.storage.models.osint import Attestation, ComplianceRun, ComplianceRule
from dags.tools import notify_slack
from dags.tools.airflow import schedule_only_for_cloud

logger = logging.getLogger("airflow.task")


def get_git_attestation(data: dict, git_sbom_type: Literal["clone", "commit"], params=None) -> list[dict]:
    engine = get_engine()

    q = (
        select(
            Attestation.id,
            Attestation.contentType,
            Attestation.sigStatus,
            Attestation.key,
            cast(Attestation.timestamp, String),
        )
        .where(Attestation.targetType == "git")
        .where(Attestation.context["git_url"].astext == data["git_url"])
        .where(Attestation.context["git_commit"].astext == data["git_commit"])
    )

    if git_sbom_type == "commit":
        q = q.where(Attestation.pipelineRun != data["pipelineRun"])
        q = q.where(Attestation.context["labels"].op("?")("is_git_commit"))

    else:
        q = q.where(Attestation.pipelineRun == data["pipelineRun"])

    row = engine.execute(q.order_by(Attestation.timestamp)).first()

    if row and row.sigStatus == "in-progress":
        raise AirflowSkipException(f"Git {git_sbom_type} SBOM is being processed. Will retry later.")

    d = {}
    if not row:
        d["status"] = "not-applicable"
        d["message"] = f"Cannot evaluate policy: Missing git {git_sbom_type} SBOM."
    elif row.sigStatus not in ["verified", "unsigned"]:  # is "unverified"
        d["attestations"].append(row.id)
        d["status"] = "not-applicable"
        d["message"] = f"Cannot evaluate policy: Git {git_sbom_type} SBOM is {row.sigStatus}."

    if d.get("status") == "not-applicable":
        q = update(ComplianceRun).values(**d).where(ComplianceRun.id == data["c_id"])
        engine.execute(q)
        raise AirflowSkipException(d["message"])

    data.setdefault("git", {})[git_sbom_type] = row._asdict()
    return data


# Search for image SBOMs to process
@task
def get_attestations(params=None) -> list[dict]:
    q = """
        SELECT 
            a.id AS id, 
            a."sigStatus",
            a."pipelineRun",
            a."context"->>'run_id' AS run_id,
            a."context"->>'sbompurl' AS sbompurl,
            a."context"->>'git_url' AS git_url,
            a."context"->>'git_commit' AS git_commit,
            a."timestamp"::TEXT AS timestamp,
            c.id AS c_id
        FROM (
            SELECT *
            FROM osint."Attestation"
            WHERE "targetType" = 'image'
            AND "sigStatus" IS DISTINCT FROM 'in-progress'
            AND "timestamp" > CURRENT_TIMESTAMP - INTERVAL '5 day'
        ) a
        LEFT JOIN osint."ComplianceRun" AS c
        ON a."pipelineRun" = c."pipelineRun"
        LEFT JOIN osint."ComplianceRule" l 
        ON c.rule = l.id
        AND l.type = 'GitIntegrity'
        WHERE c.id IS NULL
        OR (NOT c.id = ANY(c."attestations") AND c.status = 'review')
        ORDER BY id;
    """
    rows = get_engine().execute(q).all()
    return [values._asdict() for values in rows]


# Search/Create the appropriate ComplianceRun
@task
def get_compliance(data: dict, params=None) -> list[dict]:
    if not data["c_id"]:
        d = {}
        d["pipelineRun"] = select(Attestation.pipelineRun).where(Attestation.id == data["id"])
        d["rule"] = select(ComplianceRule.id).where(ComplianceRule.type == "GitIntegrity")
        d["attestations"] = [data["id"]]

        if data["sigStatus"] not in ["verified", "unsigned"]:  # if it's "unverified"
            d["status"] = "not-applicable"
            d["message"] = "Image SBOM is not verified"
        else:
            d["status"] = "review"

        data["c_id"] = (
            get_engine().execute(insert(ComplianceRun).returning(ComplianceRun.id).values(**d).inline()).first().id
        )

        if d["status"] != "review":
            raise AirflowSkipException(d["message"])

    return data


# Search for a machine git clone SBOM with similar pipelineRun
@task
def get_git_clone(data: dict, params=None) -> list[dict]:
    return get_git_attestation(data, "clone", params)


# Search for a machine git clone SBOM with different pipelineRun
# (if multiple found, choose the oldest)
@task
def get_git_commit(data: dict, params=None) -> list[dict]:
    return get_git_attestation(data, "commit", params)


# Compare git clone SBOM with git commit SBOM and update ComplianceRun.info
@task
def compare_git_sboms(data: dict, params=None) -> list[dict]:
    import json
    from pathlib import Path
    from urllib.parse import urlsplit
    from dags.tools.attestation import extract_cdx_from_signed_sbom
    from dags.tools.common import run_subprocess
    from dags.tools.fs import get_tmp_file_path
    from dags.tools.s3 import download_from_s3

    def download_sbom(d, p):
        k = urlsplit(d["key"])
        download_from_s3(key=k.path[1:], bucket_name=k.netloc, local_path=p)

        if d["contentType"] == "attest-cyclonedx-json":
            c = extract_cdx_from_signed_sbom(p)
            Path(p).write_text(json.dumps(c))

    git_clone_path = get_tmp_file_path()
    git_commit_path = get_tmp_file_path()
    git_diff_path = get_tmp_file_path()

    try:
        download_sbom(data["git"]["clone"], git_clone_path)
        download_sbom(data["git"]["commit"], git_commit_path)

        cmd = [
            Variable.get("valint_path"),
            "diff",
            git_clone_path,
            git_commit_path,
            "--output-file",
            git_diff_path,
            "-v",
        ]
        run_subprocess(cmd)
        result = json.loads(Path(git_diff_path).read_text())

        modified = result["synopsis"]["modified"]
        validated = result["synopsis"]["validated"]
        info = {
            "totalFiles": modified + validated,
            "verifiedFiles": validated,
        }
        d = {
            "info": info,
            "attestations": [
                data["id"],
                data["git"]["clone"]["id"],
                data["git"]["commit"]["id"],
            ],
        }
        change_count = info["totalFiles"] - info["verifiedFiles"]
        if change_count == 0:
            d["status"] = "pass"
        else:
            d["status"] = "fail"
            d["message"] = f"""Found {change_count} file changes between git commit and git clone SBOMs."""
        get_engine().execute(update(ComplianceRun).values(**d).where(ComplianceRun.id == data["c_id"]))

    finally:
        Path(git_clone_path).unlink(missing_ok=True)
        Path(git_commit_path).unlink(missing_ok=True)
        Path(git_diff_path).unlink(missing_ok=True)


@task_group
def process_attestation(attestation_data: dict):
    compliance = get_compliance(attestation_data)
    git_clone = get_git_clone(compliance)
    git_commit = get_git_commit(git_clone)
    comparison = compare_git_sboms(git_commit)


@dag(
    dag_id="git_intergrity",
    start_date=datetime(2023, 5, 31),
    schedule=schedule_only_for_cloud(timedelta(minutes=1)),
    max_active_runs=1,
    catchup=False,
    is_paused_upon_creation=False,
    default_args={
        "on_failure_callback": notify_slack.notify_failure,
    },
    params={},
)
def git_intergrity():
    attestations_data = get_attestations()
    process_attestation.expand(attestation_data=attestations_data)


git_intergrity()
