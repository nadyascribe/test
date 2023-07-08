import datetime
import logging
import typing

from airflow import DAG
from airflow.decorators import task

from dags import storage
from dags.storage.queries import attestations as db_attestation
from dags.storage.models import osint
from dags.tools import chain_bench, opa, github, notify_slack
from dags.tools.airflow import BaseDagParameterModel


class DagConfInput(BaseDagParameterModel):
    installation_id: int
    workflow_run_id: int
    repository_id: int
    repository_url: str
    pipeline_run_id: int
    build_script_path: str
    default_branch: str
    repo_full_name: str
    # None here is a hack to make airflow jsonschema validation not to fail if False is received
    debug: bool | None = None


logger = logging.getLogger("airflow.task")


@task(task_id="get_github_token")
def get_github_token(params: dict | None = None) -> str:
    assert params is not None
    conf = DagConfInput.parse_obj(params)
    return github.get_installation_access_token(
        conf.installation_id,
        conf.repository_id,
    )


@task(task_id="run_chainbench")
def run_chainbench(token: str, params: dict | None = None):
    assert params is not None
    conf = DagConfInput.parse_obj(params)

    sarif_data = chain_bench.run(repo_url=conf.repository_url, access_token=token)
    extract_and_save_results(conf.pipeline_run_id, sarif_data)


@task(task_id="run_opa")
def run_opa(token: str, params: dict | None = None):
    assert params is not None
    conf = DagConfInput.parse_obj(params)

    provenance_url = github.get_provenance_artifact_url(token, conf.workflow_run_id, conf.repo_full_name)
    sarif_data = opa.run(
        build_script_path=conf.build_script_path,
        protected_branch=conf.default_branch,
        repository_name=conf.repo_full_name,
        repo_url=conf.repository_url,
        token=token,
        provenance_url=provenance_url,
    )

    extract_and_save_results(conf.pipeline_run_id, sarif_data=sarif_data)


def extract_and_save_results(pipeline_run_id: int, sarif_data: dict[str, typing.Any]) -> None:
    objects: list[osint.ComplianceRun] = []
    rules = db_attestation.get_compliance_rules([o["ruleId"] for o in sarif_data["runs"][0]["results"]])
    for obj in sarif_data["runs"][0]["results"]:
        rule = rules.get(obj["ruleId"])
        if rule is None:
            logger.warning(f"Rule %s not found in the database", obj["ruleId"])
            continue
        status = obj["message"]["id"].lower()
        message = {
            "pass": rule.messagePass,
            "fail": rule.messageFail,
            "review": rule.messageReview,
            "open": rule.messageOpen,
            "not-applicable": rule.messageNotApplicable,
            "informational": rule.messageInformational,
        }[status]
        args = obj["message"].get("arguments")
        if args:
            message = message.format(*args)
        objects.append(
            osint.ComplianceRun(
                pipelineRun=pipeline_run_id,
                status=status,
                rule=rule.id,
                message=message,
            )
        )
    storage.save_objects(objects)


with DAG(
    dag_id="github-app-attestations",
    start_date=datetime.datetime(2023, 5, 15),
    schedule=None,
    catchup=False,
    params=DagConfInput.to_airflow_dag_params(),
    is_paused_upon_creation=False,
    default_args={
        "on_failure_callback": notify_slack.notify_failure,
    },
) as dag:
    get_token_task = get_github_token()
    run_chainbench_task = run_chainbench(token=get_token_task)
    run_opa_task = run_opa(token=get_token_task)
