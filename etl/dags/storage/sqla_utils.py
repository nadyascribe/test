from psycopg2.errors import FeatureNotSupported
from sqlalchemy import text
from sqlalchemy.dialects import postgresql
import sqlalchemy
from sqlalchemy.exc import NotSupportedError


_sqla_dialect = postgresql.dialect()  # type: ignore


def compile_query(q: sqlalchemy.sql.elements.ClauseElement) -> str:
    """
    Compiles sqla query (or a part of query) to a string
    :param q:
    :return:
    """
    return q.compile(dialect=_sqla_dialect, compile_kwargs={"literal_binds": True}).string


def jsonb_array_to_string(col, label: str | None = None):
    return text(
        f"""
    array_to_string(
               ARRAY(SELECT jsonb_array_elements_text({compile_query(col)}) AS jsonb_array_elements_text),
               ','::text)
    """
        + ("" if label is None else f"_{label}")
    )


def refresh_view(conn, schema_name: str, view_name: str):
    """
    Refreshes a view in the database.
    """
    try:
        conn.execute(f'refresh materialized view concurrently {schema_name}."{view_name}"')
        conn.execute(f'select 1 from {schema_name}."{view_name}" limit 1').scalar()
    except NotSupportedError as exc:
        conn.execute("rollback")
        if exc.orig is not None and isinstance(exc.orig, FeatureNotSupported):
            # if materialized view doesn't have data yet (means "view has just been created")
            # it's impossible to refresh concurrently
            conn.execute(f'refresh materialized view {schema_name}."{view_name}"')
        else:
            raise
