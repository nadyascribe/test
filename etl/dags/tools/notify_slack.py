# from airflow.providers.slack.operators.slack_webhook import SlackWebhookOperator
import requests
from urllib.parse import quote

from airflow.models import Variable

from dags.tools import env


def notify_failure(context):
    """
    Sends a Slack notification about a failed task.
    Sends only if app runs in the cloud.
    :param context:
    :return:
    """
    if env.is_not_cloud():
        return

    webhook_url = Variable.get("slack_webhook_airflow_failures")

    # Get the error details
    error = context["exception"]

    # Percent-encode the parameters
    run_id_encoded = quote(context["dag_run"].run_id, safe="")

    # Construct the Airflow URL
    airflow_url = f'http://localhost:8080/task?dag_id={context["dag"].dag_id}&task_id={context["task"].task_id}&execution_date={context["execution_date"]}'
    dag_run_url = f'http://localhost:8080/dags/{context["dag"].dag_id}/graph?run_id={run_id_encoded}&execution_date={context["execution_date"]}'

    env_name = env.environment()
    # Format the message
    message = (
        f'*Task:* {context["task"].task_id}\n'
        f'*DAG:* {context["dag"].dag_id}\n'
        f"*In environment:* {env_name}\n"
        f'*Failed on:* {context["ts"]}\n'
        f"*Error:* {repr(error)}\n"
        f"*DAG Run URL:* <{dag_run_url}|Link>   |   *Task URL:* <{airflow_url}|Link>\n"
    )

    # Send the POST request
    response = requests.post(webhook_url, json={"text": message})

    # Check the response
    if response.status_code != 200:
        raise ValueError(
            f"Request to slack returned an error {response.status_code}, the response is:\n{response.text}"
        )
