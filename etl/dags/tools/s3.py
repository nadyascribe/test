import argparse
import logging
from pathlib import Path

from airflow.providers.amazon.aws.hooks.s3 import S3Hook

from dags.tools import fs, env

parser = argparse.ArgumentParser()
parser.add_argument("--key", type=str, required=True)
parser.add_argument("--bucket_name", type=str, required=True)

logger = logging.getLogger("airflow.task")


def get_conn_id():
    if env.is_local():
        return "minio_local"
    if env.is_tests():
        return "minio_local"
    if env.is_local_docker():
        return "minio_default"
    return "aws_default"


def download_from_s3(key: str, bucket_name: str, local_path: str, conn_id: str | None = get_conn_id()) -> str:
    """
    Downloads file from S3 bucket to local path.
    May produce this warning:
     `urllib3.exceptions.HeaderParsingError: [NoBoundaryInMultipartDefect()], unparsed data: ''`
    Can be ignored if an object is downloaded.
    See https://github.com/apache/airflow/issues/29640 for details
    :param key:
    :param bucket_name:
    :param local_path:
    :param conn_id:
    :return:
    """
    hook = S3Hook(aws_conn_id=conn_id)
    logger.info("Downloading %s from bucket %s to %s", key, bucket_name, local_path)
    with open(local_path, "wb") as data:
        hook.conn.download_fileobj(bucket_name, key, data)

    return local_path


def download_to_directory(key: str, bucket: str, directory: str, conn_id: str | None = get_conn_id()) -> str:
    file_path = Path(directory) / key
    fs.ensure_directory_for_filepath(str(file_path))
    logger.debug("start downloading %s from bucket %s to %s", key, bucket, file_path)
    local_filename = download_from_s3(key, bucket, str(file_path), conn_id=conn_id)
    return local_filename
