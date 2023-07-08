from airflow.exceptions import AirflowSkipException
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator

from dags.storage import get_hook


class PostgresXcomOperator(SQLExecuteQueryOperator):
    """
    Performs specified sql and stores received result within xcom.
    """

    def __init__(self, *, fetch_one: bool, **kwargs) -> None:
        """
        :param bool fetch_one: only one row should be received.
        :param kwargs:
        """
        self.fetch_one = fetch_one
        super().__init__(**kwargs)

    def execute(self, context):  # noqa
        return get_hook().run(
            self.sql,
            parameters=self.parameters,
            handler=_fetch(fetchone=self.fetch_one),
        )


def _fetch(fetchone: bool):
    def handler(cursor):
        if not cursor.description:
            return None
        column_names = [col[0] for col in cursor.description]

        def zip_row(r):  # pylint: disable=C0103
            return dict(zip(column_names, r))

        if not fetchone:
            return [zip_row(r) for r in cursor.fetchall()]

        row = cursor.fetchone()
        if row is None:
            raise AirflowSkipException("No rows to fetch")
        return zip_row(row)

    return handler
