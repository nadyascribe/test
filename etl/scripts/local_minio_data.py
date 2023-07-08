import logging
import os
import sys
from urllib.parse import urlsplit

from sqlalchemy import select

sys.path.extend("..")

from argparse import ArgumentParser
from dags.storage import get_engine
from dags.storage.models.osint import Attestation
from dags.tools import s3
from dags.tools.fs import ensure_directory_for_filepath

parser = ArgumentParser()
parser.add_argument("--type", type=str, action="append")
parser.add_argument("--limit", type=int, default=5)
parser.add_argument("--id", type=int)
parser.add_argument("--dest", type=str, default="local_attestations")
logging.disable(logging.WARNING)


def main():
    eng = get_engine()
    args = parser.parse_args()
    conn_id = "aws_default"
    query = select(Attestation.key)
    if args.type:
        query = query.where(Attestation.contentType.in_(args.type))
    if args.id:
        query = query.where(Attestation.id == args.id)
    if args.limit:
        query = query.limit(args.limit)
    keys = list(eng.execute(query).scalars())

    print(f"found {len(keys)} keys for {args}")
    for key in keys:
        parsed = urlsplit(key)
        print("start downloading", key)
        if parsed.scheme == "s3":
            s3.download_to_directory(
                parsed.path[1:],
                parsed.netloc,
                os.path.join(args.dest, parsed.netloc),
                conn_id=conn_id,
            )
            continue

        # temp
        path = os.path.join(args.dest, "scribe-dev-filetransfers", key)
        ensure_directory_for_filepath(path)
        s3.download_from_s3(key, "scribe-dev-filetransfers", path, conn_id=conn_id)


if __name__ == "__main__":
    main()
