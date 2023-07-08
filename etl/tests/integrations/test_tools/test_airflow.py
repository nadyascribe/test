import pytest
from dags.tools import airflow


@pytest.fixture
def pydantic_model():
    class Model(airflow.BaseDagParameterModel):
        int_not_null: int
        str_not_null: str
        bool_not_null: bool
        list_not_null: list
        dict_not_null: dict
        int_null: int | None = None
        str_null: str | None = None
        bool_null: bool | None = None
        list_null: list | None = None
        dict_null: dict | None = None

    return Model


def test_pydantic_model_to_parameters(pydantic_model):
    airflow.pydantic_model_to_parameters(pydantic_model)
