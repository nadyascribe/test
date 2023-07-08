from datetime import timedelta
from typing import Type

from airflow.models import Param
from pydantic import BaseModel, root_validator

from dags.tools import env


class BaseDagParameterModel(BaseModel):
    """
    Base class for pydantic models that are used as parameters for airflow dags.
    Can convert all fields to airflow parameters using `to_airflow_dag_params` method.
    """

    @classmethod
    def to_airflow_dag_params(cls):
        return pydantic_model_to_parameters(cls)

    @root_validator
    def check_not_default(cls, values):
        """
        Checks that specified values are not default.
        :param values:
        :return:
        """
        errors = []
        for field_name, field in cls.__fields__.items():
            if field.required and is_default(field, values.get(field_name)):
                errors.append(f"{field_name} is required")
        if errors:
            raise ValueError("\n".join(errors))
        return values


def pydantic_model_to_parameters(model: Type[BaseModel]) -> dict[str, Param]:
    """
    Makes a pydantic model compatible with airflow parameters.
    Parameters are used for jsonschema validation during airflow dag runs triggered by the REST API.

    Take into account that each parameter must have a default value.
    So default values are initialized implicitly with fields' type default values. E.g. 0 for int and "" for str.
    Therefore, if value for such a field is not presented within the request, validation will be failed only during
    pydantic model initialization, see BaseDagParameterModel.check_not_default.
    :param model:
    :return:
    """
    airflow_dag_params = {}
    schema = model.schema()
    for field_name, field_schema in schema["properties"].items():
        field = model.__fields__[field_name]
        default = field.default
        if default is None and field.required:
            # airflow requires parameters to have a default value
            default = field.type_()
        type_ = field_schema["type"]
        if not field.required:
            type_ = [type_, "null"]
        airflow_dag_params[field_name] = Param(default, type=type_)
    return airflow_dag_params


def is_default(field, value):
    return _get_default(field) == value


def _get_default(field):
    default = field.default
    if default is None and field.required:
        default = field.type_()
    return default


def schedule_only_for_cloud(schedule: timedelta | None) -> timedelta | None:
    """
    Returns specified schedule only if it is not local and not disabled by env variable.
    :param schedule:
    :return:
    """
    if env.is_local() or env.no_scheduler_dags():
        return None
    return schedule
