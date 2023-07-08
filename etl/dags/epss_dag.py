import logging
from datetime import date, timedelta

import pandas as pd
import pendulum
from airflow import DAG
from airflow.models import Variable
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from sqlalchemy import Table, Column, Text, update
from sqlalchemy.dialects.postgresql import DOUBLE_PRECISION

from dags.storage import get_engine
from dags.storage.models.base import Base
from dags.storage.models import osint
from dags.tools import fs, notify_slack
from dags.tools.airflow import schedule_only_for_cloud

logger = logging.getLogger("airflow.task")


epss_temp_table = Table(
    "epss_table",
    Base.metadata,
    Column("cve", Text, nullable=False),
    Column("epss", DOUBLE_PRECISION(precision=10), nullable=False),
    Column("percentile", DOUBLE_PRECISION(precision=10), nullable=False),
    prefixes=["TEMPORARY"],
    schema="osint",
)


def epss_load(filename: str):
    df = pd.read_csv(
        filename,
        compression="gzip",
        header=1,
        sep=",",
        quotechar='"',
        error_bad_lines=False,
    )
    # with get_engine().begin() as transaction:
    transaction = get_engine()
    df.to_sql(
        name=epss_temp_table.name,
        schema="osint",
        con=transaction,
        if_exists="replace",
        index=False,
        chunksize=10000,
    )
    logger.info(f"Congrats! Data loaded from {filename} to the {epss_temp_table.name} table.")

    res = transaction.execute(
        update(osint.Vulnerability.__table__)
        .values(epssProbability=epss_temp_table.c.epss)
        .where(osint.Vulnerability.id == epss_temp_table.c.cve)
        .where(osint.Vulnerability.epssProbability.is_distinct_from(epss_temp_table.c.epss))
    )

    epss_temp_table.drop(transaction)
    logger.info("epss probabilities updated: %s", res.rowcount)


def epss_record_path():
    yesterday = date.today() - timedelta(days=1)
    ys = yesterday.strftime("%Y-%m-%d")
    shared_directory = Variable.get("shared_directory")
    epss_filename = f"{shared_directory}/epss_scores-{ys}.csv.gz"
    fs.ensure_directory_for_filepath(epss_filename)
    url = f"https://epss.cyentia.com/epss_scores-{ys}.csv.gz"
    return {"epss_filename": epss_filename, "url": url}


epss_extract = DAG(
    "epss_download",
    schedule=schedule_only_for_cloud(timedelta(days=1)),
    max_active_runs=1,
    catchup=False,
    start_date=pendulum.datetime(2022, 1, 1),
    is_paused_upon_creation=False,
    default_args={"on_failure_callback": notify_slack.notify_failure},
)

with epss_extract:
    record_path = PythonOperator(
        task_id="record-path",
        python_callable=epss_record_path,
    )

    download_task = BashOperator(
        task_id="epss-download",
        bash_command="""
        curl \
        -o {{ task_instance.xcom_pull(task_ids='record-path')['epss_filename'] }} \
        {{ task_instance.xcom_pull(task_ids='record-path')['url'] }}""",
    )

    load_data = PythonOperator(
        task_id="epss-upload",
        python_callable=epss_load,
        op_kwargs={"filename": "{{ task_instance.xcom_pull(task_ids='record-path')['epss_filename'] }}"},
    )

    teardown = PythonOperator(
        task_id="teardown",
        python_callable=fs.remove_file,
        op_kwargs={"path": "{{ task_instance.xcom_pull(task_ids='record-path')['epss_filename'] }}"},
    )

    # pylint: disable=W0104,W0106
    record_path >> download_task >> load_data >> teardown
