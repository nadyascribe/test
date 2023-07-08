import argparse
import os
import shutil
from collections import namedtuple

import airflow.settings
import pytest
from airflow.cli.commands.connection_command import connections_add
from airflow.cli.commands.db_command import initdb
from airflow.cli.commands.variable_command import variables_set
from airflow.models import DagBag
from airflow.models.taskinstance import set_current_context
from airflow.utils.context import Context
from alembic import config as alembic_config
from alembic.command import upgrade as alembic_upgrade

from dags.storage import get_session
from dags.storage.models.osint import PipelineRun


@pytest.fixture(scope="session", autouse=True)
def environ():
    os.environ["ENVIRONMENT"] = "tests"

    if "AIRFLOW__DATABASE__SQL_ALCHEMY_CONN" not in os.environ:
        os.environ["AIRFLOW__DATABASE__SQL_ALCHEMY_CONN"] = "postgresql+psycopg2://airflow:airflow@127.0.0.1/airflow"
        # reinitialize airflow settings because of changed environment variable
        airflow.settings.initialize()
    else:
        print(
            "AIRFLOW__DATABASE__SQL_ALCHEMY_CONN already set, the value is: {}".format(
                os.environ["AIRFLOW__DATABASE__SQL_ALCHEMY_CONN"]
            )
        )


@pytest.fixture(scope="session", autouse=True)
def setup_tests_environment(environ, tmp_dir):
    # session for new database
    sess = airflow.settings.Session()
    sess.execute("commit")  # close implicit transaction
    sess.execute("drop database if exists tests")
    sess.execute("create database tests")

    os.environ["AIRFLOW__DATABASE__SQL_ALCHEMY_CONN"] = "postgresql+psycopg2://airflow:airflow@127.0.0.1/tests"
    # reinitialize session because connection changed to tests database
    airflow.settings.initialize()
    sess = airflow.settings.Session()
    sess.execute("commit")  # close implicit transaction
    sess.execute(
        """
    CREATE SCHEMA osint;
    CREATE SCHEMA app;
    """
    )
    initdb([])

    _import_vars(tmp_dir)
    _import_pg_conn()
    _import_gc_conn()

    run_app_migrations()
    # as far as migrations have inserts into attestations we need to erase it
    sess.execute('truncate table osint."Attestation" CASCADE')


def _import_vars(tmp_dir):
    conn_args = argparse.ArgumentParser()
    conn_args.add_argument("key")
    conn_args.add_argument("value")
    conn_args.add_argument("--json", type=bool, required=False, default=False)
    variables_set(conn_args.parse_args(["shared_directory", tmp_dir]))
    variables_set(conn_args.parse_args(["gcs_osint_bucket", "foo"]))
    variables_set(conn_args.parse_args(["tmp_directory", tmp_dir]))
    variables_set(conn_args.parse_args(["gcs_package_version_to_project_source", "dataset.table"]))


def _import_pg_conn():
    conn_args = argparse.ArgumentParser()
    conn_args.add_argument("conn_id")
    conn_args.add_argument("--conn-uri")
    conn_args.add_argument("--conn-type")
    conn_args.add_argument("--conn-json")
    conn_args.add_argument("--conn-extra")
    conn_args.add_argument("--conn-description")
    conn_args.add_argument("--conn-host")
    conn_args.add_argument("--conn-login")
    conn_args.add_argument("--conn-port")
    conn_args.add_argument("--conn-password")
    conn_args.add_argument("--conn-schema")
    connections_add(
        conn_args.parse_args(
            args=[
                "postgres_local",
                "--conn-uri",
                "postgresql+psycopg2://airflow:airflow@127.0.0.1/tests",
                # '--conn-type', 'postgres',
            ]
        )
    )


def _import_gc_conn():
    conn_args = argparse.ArgumentParser()
    conn_args.add_argument("conn_id")
    conn_args.add_argument("--conn-uri")
    conn_args.add_argument("--conn-type")
    conn_args.add_argument("--conn-json")
    conn_args.add_argument("--conn-extra")
    conn_args.add_argument("--conn-description")
    conn_args.add_argument("--conn-host")
    conn_args.add_argument("--conn-login")
    conn_args.add_argument("--conn-port")
    conn_args.add_argument("--conn-password")
    conn_args.add_argument("--conn-schema")
    connections_add(
        conn_args.parse_args(
            args=[
                "gcs_default",
                "--conn-uri",
                "google-cloud-platform://?keyfile_dict=%7B%22auth_provider_x509_cert_url%22%3A%20%22https%3A//www.googleapis.com/oauth2/v1/certs%22%2C%20%22auth_uri%22%3A%20%22https%3A//accounts.google.com/o/oauth2/auth%22%2C%20%22client_email%22%3A%20%22mail%40mail.com%22%2C%20%22client_id%22%3A%20%22121321332132332132132%22%2C%20%22client_x509_cert_url%22%3A%20%22https%3A//www.googleapis.com/robot/v1/metadata/x509/wqwqdwdwqdwqdwdwdwdw%22%2C%20%22private_key%22%3A%20%22-----BEGIN%20PRIVATE%20KEY-----%5Cnkeykeykeykey%5Cn-----END%20PRIVATE%20KEY-----%5Cn%22%2C%20%22private_key_id%22%3A%20%22foobarbaz%22%2C%20%22project_id%22%3A%20%22proj321321321eproj%22%2C%20%22token_uri%22%3A%20%22https%3A//oauth2.googleapis.com/token%22%2C%20%22type%22%3A%20%22service_account%22%7D",
            ]
        )
    )


def run_app_migrations():
    alembic_cfg = alembic_config.Config("alembic.ini")
    alembic_upgrade(alembic_cfg, "head")


@pytest.fixture(scope="session")
def dagbag():
    return DagBag(
        dag_folder="dags",
        include_examples=False,
        collect_dags=True,
    )


@pytest.fixture()
def session():
    ses = get_session()
    yield ses
    ses.rollback()


@pytest.fixture()
def pipeline_run(session):
    pr = PipelineRun(
        productKey="test",
        version="0.0.0",
        team=1,
        pipelineName="test",
        pipelineRun="",
    )
    session.add(pr)
    session.commit()
    return pr


@pytest.fixture(autouse=True)
def airflow_context():
    t = namedtuple("t", ["run_id", "id", "map_index"])
    with set_current_context(
        Context(
            {
                "dag_run": t(1, 1, 1),
                "run_id": t(1, 1, 1),
                "task_instance": t(1, 1, 1),
            }
        )
    ):
        yield


@pytest.fixture(scope="session", autouse=True)
def tmp_dir():
    dir_ = "tests/integrations/test_data/tmp"
    if not os.path.exists(dir_):
        os.makedirs(dir_)
    yield dir_
    shutil.rmtree(dir_)
