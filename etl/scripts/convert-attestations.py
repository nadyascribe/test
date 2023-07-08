import json
import pandas as pd
from pathlib import Path
from argparse import ArgumentParser


def snake_to_camel(s):
    t = s.split("_")
    res = t[0] + "".join(e.title() for e in t[1:])
    return str(res)


def load_stab(filename):
    d = json.loads(Path(filename).read_text())
    df = pd.DataFrame(columns=d["columns"], data=d["data"])

    df.key = df.cloud_storage + "://" + df.bucket.astype(str) + "/" + df.key.astype(str)
    df.content_type = df.content_type.replace("sarif-slsa", "SLSA").replace("ssdf", "SSDF")
    df.context_type = df.context_type.replace("githubApp", "Github_App")
    df = df.drop(
        columns=[
            "file_id",
            "status",
            "cloud_storage",
            "bucket",
            "lock",
            "access_time",
            "updated_at",
        ]
    )
    df = df.rename(columns={"metadata": "context", "created_at": "timestamp"})
    df.columns = df.columns.map(snake_to_camel)
    df["teamId"] = None
    df["validated"] = None
    df["license"] = None
    df["txt"] = None

    df = df.reindex(
        columns=[
            "contentType",
            "contextType",
            "context",
            "key",
            "timestamp",
            "userId",
            "teamId",
            "validated",
            "license",
            "txt",
        ]
    )

    # TEMP workaround: invalid input syntax for type bigint
    df["userId"] = None

    return df


def gen_sql(df):
    sql = []
    for i, row in df.iterrows():
        cols = json.dumps(df.columns.to_list())[1:-1]
        vals = repr(row.values.flatten().tolist())[1:-1].replace(" None", " null")
        s = f'INSERT INTO "Attestation" ({cols}) VALUES ({vals});'
        sql.append(s)

    return sql


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("filename")
    args = parser.parse_args()

    filename = args.filename
    df = load_stab(filename)
    sql = gen_sql(df)

    for l in sql:
        print(l)
