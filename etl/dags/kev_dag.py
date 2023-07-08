import pandas as pd
import pendulum
from airflow import DAG
from airflow.models import Variable
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

from dags.storage import get_hook
from dags.tools import fs, notify_slack

kev_extract = DAG(
    "kev_extract",
    schedule=None,
    max_active_runs=1,
    catchup=False,
    start_date=pendulum.datetime(2022, 1, 1),
    default_args={
        "on_failure_callback": notify_slack.notify_failure,
    },
)


table_name = "kev_table"


def kev_load(filename: str):
    print(f"kev filename {filename}")
    df = pd.read_csv(filename, sep=",", quotechar='"', error_bad_lines=False)
    pg_hook = get_hook()
    engine = pg_hook.get_sqlalchemy_engine()

    df.to_sql(name=table_name, con=engine, if_exists="replace", index=False, chunksize=10000)

    print(f"Congrats! Data loaded from {filename} to the {table_name} table.")


def record_path(url, filename):
    shared_directory = Variable.get("shared_directory")
    path = f"{shared_directory}/{filename}"
    return {"path": path, "url": url}


with kev_extract:
    record_path = PythonOperator(
        task_id="record-path",
        python_callable=record_path,
        op_kwargs={
            "url": "https://www.cisa.gov/sites/default/files/csv/known_exploited_vulnerabilities.csv",
            "filename": "known_exploited_vulnerabilities.csv",
        },
    )

    download_task = BashOperator(
        task_id="epss-download",
        bash_command="""
        curl \
        -o {{ task_instance.xcom_pull(task_ids='record-path')['path'] }} \
        {{ task_instance.xcom_pull(task_ids='record-path')['url'] }}""",
    )

    load_data = PythonOperator(
        task_id="kev-load",
        python_callable=kev_load,
        op_kwargs={"filename": "{{ task_instance.xcom_pull(task_ids='record-path')['path'] }}"},
    )

    teardown = PythonOperator(
        task_id="teardown",
        python_callable=fs.remove_file,
        op_kwargs={"path": "{{ task_instance.xcom_pull(task_ids='record-path')['path'] }}"},
    )

    # pylint: disable=W0104,W0106
    record_path >> download_task >> load_data >> teardown
