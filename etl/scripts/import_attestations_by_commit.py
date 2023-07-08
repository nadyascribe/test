# %%
import pandas as pd
import sqlalchemy
import argparse
import boto3


# %%
def get_aws_param(env, name):
    client = boto3.client("ssm")
    p = client.get_parameter(Name=f"/{env}/airflow/{name}", WithDecryption=True)
    return p["Parameter"]["Value"]


# %%
def get_dev_pipeline_runs(engine, commit):
    q = f"""
    SELECT DISTINCT p.*
    FROM osint."Attestation" a
    LEFT JOIN osint."PipelineRun" p
    ON p.id = a."pipelineRun"
    WHERE a."context"->>'git_commit' = '{commit}'
    ORDER BY p.id
    """
    return pd.read_sql(q, con=engine)


# %%
def get_dev_attestations(engine, commit):
    q = f"""
    SELECT *
    FROM osint."Attestation"
    WHERE "context"->>'git_commit' = '{commit}'
    ORDER BY id
    """
    return pd.read_sql(q, con=engine)


# %%
def add_local_pipeline_runs(engine, ppln_dev):
    ppln_local = ppln_dev.drop(["id"], axis=1)
    c = ppln_local.to_sql(
        "PipelineRun",
        con=engine,
        schema="osint",
        if_exists="append",
        index=False,
        dtype={"context": sqlalchemy.types.JSON},
    )
    return pd.read_sql_table("PipelineRun", con=engine, schema="osint")[-c:].id


# %%
def add_local_attestations(engine, atts_dev, ppln_ids):
    dev_ids = atts_dev.pipelineRun.unique()
    ppln_mapping = dict([*zip(dev_ids, ppln_ids)])

    atts_local = atts_dev.drop(["id", "txt", "project"], axis=1, errors="ignore")
    atts_local.replace({"pipelineRun": ppln_mapping}, inplace=True)
    c = atts_local.to_sql(
        "Attestation",
        con=engine_local,
        schema="osint",
        if_exists="append",
        index=False,
        dtype={"context": sqlalchemy.types.JSON},
    )
    return pd.read_sql_table("Attestation", con=engine, schema="osint")[-c:].id


# %%
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--commit", required=True, help="git commit to filter attestations by")
    args = parser.parse_args()
    commit = args.commit

    dev_pass = get_aws_param("dev", "POSTGRES_PASSWORD")
    engine_dev = sqlalchemy.create_engine(f"postgresql+psycopg2://airflow:{dev_pass}@localhost:6432/airflow")
    ppln_dev = get_dev_pipeline_runs(engine_dev, commit)
    atts_dev = get_dev_attestations(engine_dev, commit)

    engine_local = sqlalchemy.create_engine("postgresql+psycopg2://airflow:airflow@localhost:5432/airflow")
    ppln_ids = add_local_pipeline_runs(engine_local, ppln_dev)
    print("ppln_ids:", list(ppln_ids))
    atts_ids = add_local_attestations(engine_local, atts_dev, ppln_ids)
    print("atts_ids:", list(atts_ids))


# %%
