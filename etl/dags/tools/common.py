import pendulum
import logging

from airflow.operators.python import get_current_context
from airflow.hooks.subprocess import SubprocessHook
from airflow.exceptions import AirflowFailException


logger = logging.getLogger("airflow.task")


# recursively overwrite values in 'a' with none 'None' values from 'b'
# if both are dict, iterate (and recurse) over their shared keys
# if 'b' is empty, stop recursing and return 'a'
def merge_dicts(a: dict, b: dict) -> dict:
    if type(a) == type(b) is dict:
        d = {}
        for k in set([*a.keys(), *b.keys()]):
            d[k] = merge_dicts(a.get(k), b.get(k))
        return d
    return a if b in [None, [], {}] else b


def make_job_id():
    context = get_current_context()
    return "{dag_run_id}__{map_index}".format(
        dag_run_id=context["dag_run"].run_id,
        map_index=context["task_instance"].map_index,
    )


def get_dag_run_timestamp():
    context = get_current_context()
    run_id = context["dag_run"].run_id
    return pendulum.parse(run_id.split("__")[1]).int_timestamp


def run_subprocess(cmd: list, env: dict[str, str] | None = None) -> None:
    result = SubprocessHook().run_command(cmd, env)
    if result.exit_code != 0:
        logger.error("SubprocessHook error: %s", result.output)
        raise AirflowFailException("SubprocessHook failed")
