"""
Contains all storage operations, such as raw SQL queries and some functions that can be used to store data inside of DB.
"""
from __future__ import annotations

from typing import Optional, Any

import psycopg2.extensions
import psycopg2.extras
from airflow.operators.python import PythonOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook
from sqlalchemy import Column
from sqlalchemy.dialects.postgresql import insert, Insert
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from dags.storage.models.base import Base
from dags.tools import env

_engines = {}
psycopg2.extensions.register_adapter(dict, psycopg2.extras.Json)


def get_hook(conn_id: Optional[str] = None) -> PostgresHook:
    """
    Returns airflow postgres hook using specified connection id or a default one
    :param conn_id:
    :return:
    """
    return PostgresHook(postgres_conn_id=conn_id or get_db_conn_id())


def get_db_conn_id():
    """
    Returns connection id for the DB
    :return:
    """
    if env.tests_or_local():
        return "postgres_local"
    return "postgres_default"


def get_session(conn_id: Optional[str] = None) -> Session:
    """
    Returns sqlalchemy session using specified connection id or a default one.
    Beware: shouldn't be called within different function of one task, because each call creates a new session.
    :param conn_id:
    :return:
    """
    return sessionmaker(bind=get_engine(conn_id=conn_id))()


def get_engine(conn_id: Optional[str] = None) -> Engine:
    """
    Returns sqlalchemy engine using specified connection id or a default one.
    :param conn_id:
    :return:
    """
    if conn_id not in _engines:
        hook = get_hook(conn_id=conn_id)
        _engines[conn_id] = hook.get_sqlalchemy_engine()
    return _engines[conn_id]


class SQLAlchemyOperator(PythonOperator):
    """
    PythonOperator with SQLAlchemy session management - creates session for the Python callable
    and commit/rollback it afterwards.

    Set `conn_id` with you DB connection.

    Pass `session` parameter to the python callable.
    """

    def execute_callable(self):
        session = get_session(get_db_conn_id())
        try:
            result = self.python_callable(*self.op_args, session=session, **self.op_kwargs)
            session.commit()
        except Exception:
            session.rollback()
            raise
        return result


def make_upsert_query(model: Base, index_columns: list, upsert_cols: list[Column] | None = None) -> Insert:
    """
    Creates upsert (insert ... on conflict... do update) query for the model
    :param model: model to upsert
    :param index_columns: list of columns for `on conflict` clause
    :param upsert_cols: columns to update on conflict. If None, all columns except primary key and computed columns will be updated
    :return:
    """
    insert_query = insert(model)
    res = {}
    table = model.__table__
    upsert_cols = {c.name for c in upsert_cols} if upsert_cols is not None else None
    pkey_cols = set(table.primary_key.columns.keys())
    for column_name, column in table.columns.items():
        if column_name in pkey_cols:
            continue
        if column_name in index_columns:
            continue
        if column.computed is not None:
            continue
        if upsert_cols is not None and column_name not in upsert_cols:
            continue
        res[column_name] = getattr(insert_query.excluded, column_name)
    return insert_query.on_conflict_do_update(
        index_elements=index_columns,
        set_=res,
    )


def model_as_dict(model: Base, db_names: bool = True) -> dict[str, Any]:
    """
    Converts a model object to dict
    :param model:
    :param db_names: result dict will contain table column names instead of model field names
    :return:
    """
    res = {}
    for field_name, col in model.__mapper__.columns.items():
        if col.computed is not None:
            continue
        value = getattr(model, field_name)
        if value is None and not col.nullable and col.server_default is not None:
            continue
        res[col.name if db_names else field_name] = value
    for col_name, col_value in model.__table__.primary_key.columns.items():
        if col_value.identity is not None:
            res.pop(col_name, None)
    return res


def save_objects(deps: list[Base]):
    ses = get_session()
    ses.bulk_save_objects(deps)
    ses.commit()
