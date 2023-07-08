from airflow.providers.google.cloud.hooks.bigquery import BigQueryHook
from airflow.providers.google.cloud.hooks.gcs import GCSHook


def get_hook():
    """
    Returns GCSHook with default connection id
    :return:
    """
    return GCSHook(gcp_conn_id=get_conn_id())


def get_bq_hook():
    """
    Returns BigQueryHook with default connection id
    :return:
    """
    return BigQueryHook(gcp_conn_id=get_conn_id())


def get_conn_id():
    return "gcs_default"
