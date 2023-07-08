from datetime import timedelta
import logging
import pendulum

from sqlalchemy import (
    CHAR,
    INTEGER,
    BIGINT,
    Column,
    Identity,
    MetaData,
    Table,
    func,
    select,
)

from airflow.decorators import task, dag
from airflow.exceptions import AirflowFailException
from airflow.utils.state import State
from airflow.utils.trigger_rule import TriggerRule

from dags.storage import get_engine
from dags.storage.models.osint import Component, VulAdvisory, VulComponent
from dags.storage.models.base import Base
from dags.tools.airflow import schedule_only_for_cloud

logger = logging.getLogger("airflow.task")

CVE_CPE_TABLE_NAME = "cve_cpe"
PRODUCT_CPE_TABLE_NAME = "product_cpe"
POPULATE_CPE_PARTS_FUNCTION_NAME = "populate_cpe_parts"
POPULATE_CPE_CVE_PARTS_TRIGGER_NAME = "populate_cve_cpe_parts"
POPULATE_PRODCUCT_CVE_PARTS_TRIGGER_NAME = "populate_product_cpe_parts"
CPE_JOIN_VIEW_NAME = "cpe_join_materialized_view"

SCHEMA_NAME = "osint"

# cve_cpe tmp table
_cve_cpe = None


def get_cve_cpe():
    global _cve_cpe
    if _cve_cpe is None:
        _cve_cpe = Table(
            CVE_CPE_TABLE_NAME,
            Base.metadata,
            Column(
                "id",
                INTEGER,
                Identity(
                    always=True,
                    start=1,
                    increment=1,
                    minvalue=1,
                    maxvalue=2147483647,
                    cycle=False,
                    cache=1,
                ),
                primary_key=True,
            ),
            Column("cve", CHAR(32), nullable=False),
            Column("cpe", CHAR(256), nullable=False),
            Column("part1", CHAR(16), index=True),
            Column("part2", CHAR(16), index=True),
            Column("part3", CHAR(16), index=True),
            Column("part4", CHAR(16), index=True),
            Column("part5", CHAR(16), index=True),
            Column("part6", CHAR(16), index=True),
            Column("part7", CHAR(16), index=True),
            Column("part8", CHAR(16), index=True),
            Column("part9", CHAR(16), index=True),
            Column("part10", CHAR(16), index=True),
            Column("part11", CHAR(16), index=True),
            schema=SCHEMA_NAME,
        )

    return _cve_cpe


# product_cpe tmp table
_product_cpe = None


def get_product_cpe():
    global _product_cpe
    if _product_cpe is None:
        _product_cpe = Table(
            PRODUCT_CPE_TABLE_NAME,
            Base.metadata,
            Column(
                "id",
                INTEGER,
                Identity(
                    always=True,
                    start=1,
                    increment=1,
                    minvalue=1,
                    maxvalue=2147483647,
                    cycle=False,
                    cache=1,
                ),
                primary_key=True,
            ),
            Column("component", BIGINT, nullable=False),
            Column("cpe", CHAR(256), nullable=False),
            Column("part1", CHAR(16), index=True),
            Column("part2", CHAR(16), index=True),
            Column("part3", CHAR(16), index=True),
            Column("part4", CHAR(16), index=True),
            Column("part5", CHAR(16), index=True),
            Column("part6", CHAR(16), index=True),
            Column("part7", CHAR(16), index=True),
            Column("part8", CHAR(16), index=True),
            Column("part9", CHAR(16), index=True),
            Column("part10", CHAR(16), index=True),
            Column("part11", CHAR(16), index=True),
            schema=SCHEMA_NAME,
        )

    return _product_cpe


@task
def create_tmp_tables() -> MetaData:
    engine = get_engine()

    # create tmp tables
    get_cve_cpe().create(engine, checkfirst=True)
    get_product_cpe().create(engine, checkfirst=True)

    # create function and triggers
    populate_cve_parts_func = f"""
        CREATE OR REPLACE FUNCTION {SCHEMA_NAME}.{POPULATE_CPE_PARTS_FUNCTION_NAME}()
        RETURNS TRIGGER AS $$
        DECLARE
            cpe_normalized TEXT;
            parts TEXT[];
        BEGIN
            cpe_normalized := regexp_replace(LOWER(NEW.cpe), '^cpe:2\.3:', '', 'g');
            cpe_normalized := regexp_replace(cpe_normalized, '[-]', '_', 'g');
            cpe_normalized := regexp_replace(cpe_normalized, '[^a-z0-9:_]', '', 'g');
            parts := string_to_array(cpe_normalized, ':');
            
            FOR i IN 1 .. array_length(parts, 1) LOOP
                parts[i] := NULLIF(SUBSTRING(parts[i] FROM 1 FOR 16), '');
            END LOOP;

            NEW.part1 := parts[1];
            NEW.part2 := parts[2];
            NEW.part3 := parts[3];
            NEW.part4 := parts[4];
            NEW.part5 := parts[5];
            NEW.part6 := parts[6];
            NEW.part7 := parts[7];
            NEW.part8 := parts[8];
            NEW.part9 := parts[9];
            NEW.part10 := parts[10];
            NEW.part11 := parts[11];

            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """
    engine.execute(populate_cve_parts_func)

    cve_cpe_trigger = f"""
        CREATE TRIGGER {POPULATE_CPE_CVE_PARTS_TRIGGER_NAME}
            BEFORE INSERT OR UPDATE ON {SCHEMA_NAME}.{CVE_CPE_TABLE_NAME}
            FOR EACH ROW
            EXECUTE FUNCTION {SCHEMA_NAME}.{POPULATE_CPE_PARTS_FUNCTION_NAME}();
    """
    engine.execute(cve_cpe_trigger)

    product_cpe_trigger = f"""
        CREATE TRIGGER {POPULATE_PRODCUCT_CVE_PARTS_TRIGGER_NAME}
            BEFORE INSERT OR UPDATE ON {SCHEMA_NAME}.{PRODUCT_CPE_TABLE_NAME}
            FOR EACH ROW
            EXECUTE FUNCTION {SCHEMA_NAME}.{POPULATE_CPE_PARTS_FUNCTION_NAME}();
    """
    engine.execute(product_cpe_trigger)

    # create view
    cpe_join_view = f"""
        CREATE MATERIALIZED VIEW IF NOT EXISTS {SCHEMA_NAME}.{CPE_JOIN_VIEW_NAME} AS
            SELECT DISTINCT cve, component
            FROM (
                SELECT cc.cve, pc.component
                FROM {SCHEMA_NAME}.{CVE_CPE_TABLE_NAME} cc
                    INNER JOIN {SCHEMA_NAME}.{PRODUCT_CPE_TABLE_NAME} pc ON
                        (cc.part1 IS NULL OR pc.part1 IS NULL OR cc.part1 = pc.part1)
                        AND (cc.part2 = pc.part2)
                        AND (cc.part3 IS NULL OR pc.part3 IS NULL OR cc.part3 = pc.part3)
                        AND (cc.part4 IS NULL OR pc.part4 IS NULL OR cc.part4 = pc.part4)
                        AND (cc.part5 IS NULL OR pc.part5 IS NULL OR cc.part5 = pc.part5)
                        AND (cc.part6 IS NULL OR pc.part6 IS NULL OR cc.part6 = pc.part6)
                        AND (cc.part7 IS NULL OR pc.part7 IS NULL OR cc.part7 = pc.part7)
                        AND (cc.part8 IS NULL OR pc.part8 IS NULL OR cc.part8 = pc.part8)
                        AND (cc.part9 IS NULL OR pc.part9 IS NULL OR cc.part9 = pc.part9)
                        AND (cc.part10 IS NULL OR pc.part10 IS NULL OR cc.part10 = pc.part10)
                        AND (cc.part11 IS NULL OR pc.part11 IS NULL OR cc.part11 = pc.part11)
                UNION 
                SELECT cc.cve, pc.component
                FROM {SCHEMA_NAME}.{CVE_CPE_TABLE_NAME} cc
                    INNER JOIN {SCHEMA_NAME}.{PRODUCT_CPE_TABLE_NAME} pc ON
                        (cc.part1 IS NULL OR pc.part1 IS NULL OR cc.part1 = pc.part1)
                        AND (cc.part2 IS NULL)
                        AND (cc.part3 IS NULL OR pc.part3 IS NULL OR cc.part3 = pc.part3)
                        AND (cc.part4 IS NULL OR pc.part4 IS NULL OR cc.part4 = pc.part4)
                        AND (cc.part5 IS NULL OR pc.part5 IS NULL OR cc.part5 = pc.part5)
                        AND (cc.part6 IS NULL OR pc.part6 IS NULL OR cc.part6 = pc.part6)
                        AND (cc.part7 IS NULL OR pc.part7 IS NULL OR cc.part7 = pc.part7)
                        AND (cc.part8 IS NULL OR pc.part8 IS NULL OR cc.part8 = pc.part8)
                        AND (cc.part9 IS NULL OR pc.part9 IS NULL OR cc.part9 = pc.part9)
                        AND (cc.part10 IS NULL OR pc.part10 IS NULL OR cc.part10 = pc.part10)
                        AND (cc.part11 IS NULL OR pc.part11 IS NULL OR cc.part11 = pc.part11)
                UNION 
                SELECT cc.cve, pc.component
                FROM {SCHEMA_NAME}.{CVE_CPE_TABLE_NAME} cc
                    INNER JOIN {SCHEMA_NAME}.{PRODUCT_CPE_TABLE_NAME} pc ON
                        (cc.part1 IS NULL OR pc.part1 IS NULL OR cc.part1 = pc.part1)
                        AND (pc.part2 IS NULL)
                        AND (cc.part3 IS NULL OR pc.part3 IS NULL OR cc.part3 = pc.part3)
                        AND (cc.part4 IS NULL OR pc.part4 IS NULL OR cc.part4 = pc.part4)
                        AND (cc.part5 IS NULL OR pc.part5 IS NULL OR cc.part5 = pc.part5)
                        AND (cc.part6 IS NULL OR pc.part6 IS NULL OR cc.part6 = pc.part6)
                        AND (cc.part7 IS NULL OR pc.part7 IS NULL OR cc.part7 = pc.part7)
                        AND (cc.part8 IS NULL OR pc.part8 IS NULL OR cc.part8 = pc.part8)
                        AND (cc.part9 IS NULL OR pc.part9 IS NULL OR cc.part9 = pc.part9)
                        AND (cc.part10 IS NULL OR pc.part10 IS NULL OR cc.part10 = pc.part10)
                        AND (cc.part11 IS NULL OR pc.part11 IS NULL OR cc.part11 = pc.part11)
                ) q;
    """
    engine.execute(cpe_join_view)

    logger.info("Created temporary DB constructs")


@task
def update_cve_cpe():
    select_stmt = select(VulAdvisory.vulId, Column("unnested_cpe")).select_from(
        func.unnest(VulAdvisory.cpes).alias("unnested_cpe")
    )
    insert_stmt = get_cve_cpe().insert().from_select(["cve", "cpe"], select_stmt)

    with get_engine().begin() as transaction:
        transaction.execute(insert_stmt)


@task
def update_product_cpe():
    select_stmt = select(Component.id, Column("unnested_cpe")).select_from(
        func.unnest(Component.cpes).alias("unnested_cpe")
    )
    insert_stmt = get_product_cpe().insert().from_select(["component", "cpe"], select_stmt)

    with get_engine().begin() as transaction:
        transaction.execute(insert_stmt)


@task
def update_vul_component():
    engine = get_engine()
    # refresh materialized view
    engine.execute(f"REFRESH MATERIALIZED VIEW {SCHEMA_NAME}.{CPE_JOIN_VIEW_NAME}")

    with engine.begin() as transaction:
        # Insert new product vulnerabilities
        ret = transaction.execute(
            f'INSERT INTO {SCHEMA_NAME}."{VulComponent.__tablename__}" (component, "vulId") (SELECT component, cve FROM {SCHEMA_NAME}.{CPE_JOIN_VIEW_NAME} WHERE (component, cve) NOT IN (SELECT component, "vulId" FROM {SCHEMA_NAME}."{VulComponent.__tablename__}" WHERE deleted IS NULL))'
        )
        logger.info(f"Inserted {ret.rowcount} new product vulnerability records into VulComponent")

        # Mark removed product vulnerabilities
        ret = transaction.execute(
            f'UPDATE {SCHEMA_NAME}."{VulComponent.__tablename__}" SET deleted = NOW() WHERE (component, "vulId") NOT IN (SELECT component, cve FROM {SCHEMA_NAME}.{CPE_JOIN_VIEW_NAME}) AND deleted IS NULL'
        )
        logger.info(f"Marked {ret.rowcount} removed product vulnerability records in VulComponent")


@task(trigger_rule=TriggerRule.ALL_DONE)
def drop_tmp_tables():
    engine = get_engine()

    # drop materializzed view
    engine.execute(f"DROP MATERIALIZED VIEW IF EXISTS {SCHEMA_NAME}.{CPE_JOIN_VIEW_NAME}")

    # drop tables (and triggers)
    get_cve_cpe().drop(bind=engine, checkfirst=True)
    get_product_cpe().drop(bind=engine, checkfirst=True)

    # drop function
    engine.execute(f"DROP FUNCTION IF EXISTS {SCHEMA_NAME}.{POPULATE_CPE_PARTS_FUNCTION_NAME}")

    logger.info("Dropped temporary DB constructs")


@task(trigger_rule=TriggerRule.ALL_DONE)
def success_check(**kwargs):
    for task_instance in kwargs["dag_run"].get_task_instances():
        if task_instance.current_state() == State.FAILED:
            raise AirflowFailException(f"{task_instance.task_id} has failed, failing DAG run")


@dag(
    "update_vuln_components",
    start_date=pendulum.datetime(2021, 1, 1, tz="UTC"),
    schedule=schedule_only_for_cloud(timedelta(hours=6)),
    catchup=False,
    max_active_runs=1,
)
def update_vuln_components():
    create_task = create_tmp_tables()
    update_cve_cpe_task = update_cve_cpe()
    update_product_cpe_task = update_product_cpe()
    update_vul_component_task = update_vul_component()
    drop_task = drop_tmp_tables()
    success_check_task = success_check()

    (
        create_task
        >> [update_cve_cpe_task, update_product_cpe_task]
        >> update_vul_component_task
        >> drop_task
        >> success_check_task
    )


update_vuln_components()
