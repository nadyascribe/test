# Collect all epss scores over time, and not only the current scores.
# Needed for analysis of the accumulated epss scores over time.

# Concept:
# 1. Maintain a table with a list of all dates for which epss scores are available.
# 2. Maintain a table with a list of all epss scores for all dates.
# 3. When running the DAG, fill the dates table with all dates since last date in the table.
# 4. For each date in the dates table, download the epss scores for that date,
#    and append to the epss scores table, while adding the date to the epss scores table.

# See here for a reference on running a list of tasks:
# https://stackoverflow.com/questions/71144263/airflow-tasks-iterating-over-list-should-run-sequentially

from datetime import datetime, timedelta

import pandas as pd
import pendulum
from airflow import DAG
from airflow.decorators import task
from airflow.operators.python import PythonOperator
from dags.tools import notify_slack

from dags.storage import get_hook, get_engine

accumulating_epss_update_dates = DAG(
    "accumulating_epss_update_dates",
    schedule=None,
    description="Collect all epss scores over time, and not only the current scores.",
    start_date=pendulum.datetime(2022, 1, 1),
    max_active_runs=1,
    catchup=False,
    default_args={
        "on_failure_callback": notify_slack.notify_failure,
    },
)

EPSS_DATES_TABLE_NAME = "epss_dates_table"
# TODO: decide on a date to start from. I  thing 2022 02 10 is a good start date
INITIAL_DATE = pendulum.datetime(2023, 2, 20, tz="UTC")


def epss_update_dates():
    engine = get_engine()
    # Create table if it does not exist.
    # Table should have a date column and a "handled" true/false column.
    # The "handled" column is used to indicate that the date has been processed and will defult to false
    engine.execute(f"CREATE TABLE IF NOT EXISTS {EPSS_DATES_TABLE_NAME} (date date, handled boolean default false);")

    df = pd.read_sql_table(EPSS_DATES_TABLE_NAME, engine)
    print(f"Current dates table: {df}")
    if df.empty:
        print("Dates table is empty. Adding initial.")
        df = pd.DataFrame([[INITIAL_DATE, False]], columns=["date", "handled"])
        df.to_sql(
            name=EPSS_DATES_TABLE_NAME,
            con=engine,
            if_exists="replace",
            index=False,
            chunksize=10000,
        )
        print("Initial date added to table.")

    # Get the last date in the table
    last_date = df["date"].max()
    print(f"Last date in table: {last_date}")
    # Avoid duplicates by adding one day to the last date
    last_date += timedelta(days=1)

    # Get all dates since the last date in the table
    # Get all dates since the last date in the table
    yesterday = pendulum.today(tz=last_date.tz) - timedelta(days=1)
    yesterday = pd.to_datetime(yesterday).tz_convert(last_date.tz)
    dates = pd.date_range(start=last_date, end=yesterday)
    print(f"Number of new dates added {len(dates)}")
    # Add handled column to the dates list with value False
    dates = list(zip(dates, [False] * len(dates)))

    # Add the new dates to the table and mark them as not handled
    df = df.append(pd.DataFrame(dates, columns=["date", "handled"]), ignore_index=True)
    df.to_sql(
        name=EPSS_DATES_TABLE_NAME,
        con=engine,
        if_exists="replace",
        index=False,
        chunksize=10000,
    )
    print("New dates added to table.")


@task
def epss_get_dates():
    """
    Get all dates from the dates table that have not been handled yet.
    Return a list of dates."""
    pg_hook = get_hook()
    engine = pg_hook.get_sqlalchemy_engine()
    # Create table if it does not exist.
    engine.execute(f"CREATE TABLE IF NOT EXISTS {EPSS_DATES_TABLE_NAME} (date date, handled boolean default false);")
    df = pd.read_sql_table(EPSS_DATES_TABLE_NAME, engine)
    # Get all dates that have not been handled yet
    df = df[df["handled"] == False]
    return list(map(lambda x: x.to_pydatetime().isoformat(), df["date"]))


@task
def epss_download(task_date):
    """
    Download epss scores file for a given date.
    Push to the database.
    Delete the file.
    """
    task_date = datetime.fromisoformat(task_date)
    date_str = task_date.date().isoformat()
    print(f"Processing date: {date_str}")
    URL = f"https://epss.cyentia.com/epss_scores-{date_str}.csv.gz"
    table_name = "accumulated_epss_table"
    # Create table if does not exist.
    # Table columns: cve, score, percentiles, date
    pg_hook = get_hook()
    engine = pg_hook.get_sqlalchemy_engine()
    engine.execute(f"CREATE TABLE IF NOT EXISTS {table_name} (cve text, epss float, percentile float, date date);")

    # Download the file
    print(f"reading file from {URL}")
    # Load file to dataframe
    df = pd.read_csv(URL, compression="gzip", header=1, sep=",", quotechar='"', error_bad_lines=False)
    # Add date column
    df["date"] = task_date
    # Push to database
    df.to_sql(name=table_name, con=engine, if_exists="append", index=False, chunksize=10000)
    print(f"Congrats! Data loaded to the {table_name} table.")
    # Update the date table to indicate that the date has been processed
    engine.execute(f"UPDATE {EPSS_DATES_TABLE_NAME} SET handled = true WHERE date = '{task_date}';")


with accumulating_epss_update_dates:
    update_dates_task = PythonOperator(
        task_id="update-dates",
        python_callable=epss_update_dates,
    )

    # pylint: disable=W0106
    update_dates_task >> epss_download.expand(task_date=epss_get_dates())
