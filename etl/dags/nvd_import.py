import json
import logging
from datetime import datetime, timedelta
from pathlib import Path

from airflow import DAG
from airflow.decorators import task
from airflow.models import Variable, DagRun

from dags.domain.advisory.nvd import service as nvd_service
from dags.storage import get_engine
from dags.storage.queries import vuln_advisories
from dags.tools import fs, env, notify_slack
from dags.tools.airflow import schedule_only_for_cloud

logger = logging.getLogger("airflow.task")


def _make_filename(base_dir: str, batch_number: int) -> str:
    return str(Path(base_dir) / "nvd" / f"cves-{batch_number}.json")


def _dump(batch_number: int, batch: list[dict]) -> str:
    file_name = _make_filename(Variable.get("shared_directory"), batch_number)
    fs.ensure_directory_for_filepath(str(file_name))
    with open(file_name, "w") as f:
        json.dump(batch, f)
    return file_name


with DAG(
    dag_id="nvds_import",
    start_date=datetime(2023, 2, 21),
    schedule=schedule_only_for_cloud(timedelta(days=1)),
    max_active_runs=1,
    catchup=False,
    description="import data from nvds database",
    is_paused_upon_creation=False,
    default_args={
        "on_failure_callback": notify_slack.notify_failure,
    },
) as dag:

    @task(task_id="run_imports")
    def run_download(dag_run: DagRun | None = None) -> list[str]:
        latest_pub = vuln_advisories.get_latest_pub_date()
        logger.info("latest pub date: %s", latest_pub)

        latest_mod = vuln_advisories.get_latest_update_date()
        logger.info("latest mod date: %s", latest_mod)

        params = nvd_service.Params(
            latest_pub_date=latest_pub,
            latest_mod_date=latest_mod,
            limit_results=dag_run.conf.get("limit") or env.cloud_imports_limit(),
        )
        results = []
        total_received_results = 0
        retries = 5
        batch_number = 0
        total_results = 0
        files = []
        while True:
            try:
                batch, total_results = nvd_service.download_cves(params)
                logger.info("%s records received", len(batch))
            except Exception as e:
                logger.exception(e)
                retries -= 1
                if retries == 0:
                    raise
                continue
            retries = 5
            results.extend(batch)
            total_received_results += len(batch)

            if len(results) >= 10000:
                files.append(_dump(batch_number, results))
                results.clear()
                batch_number += 1
            if not params.prepare_for_next_request(total_received_results, total_results):
                logger.info("nvd requests stopped")
                break

        files.append(_dump(batch_number, results))
        return files

    @task(task_id="export_to_db_and_cleanup")
    def export_to_db_and_cleanup(file_names):
        with get_engine().begin() as transaction:
            for file_name in file_names:
                logger.info('importing file "%s" to db', file_name)
                vuln_advisories.import_file_to_db(transaction, file_name)

        # do it separately because of transaction above
        for file_name in file_names:
            fs.remove_file(file_name)

    export_to_db_and_cleanup(file_names=run_download())
