import pytest
from airflow.models import DagBag
from airflow.utils.dag_cycle_tester import check_cycle


def test_tasks_parsed():
    dagbag = DagBag(
        dag_folder="dags",
        include_examples=False,
        collect_dags=False,
    )
    dagbag.collect_dags(dag_folder="dags", include_examples=False)
    for dag in dagbag.dags.values():
        check_cycle(dag)
    for name, err in dagbag.import_errors.items():
        print(name)
        print(err)
    assert not dagbag.import_errors
