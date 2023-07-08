import os
import sys

sys.path.extend("..")

from dags.nvd_import import export_to_db_and_cleanup
from argparse import ArgumentParser

parser = ArgumentParser()
parser.add_argument("--path", type=str, default="shared/nvd")


def main():
    args = parser.parse_args()
    file_names = [os.path.join(args.path, el) for el in os.listdir(args.path)]
    export_to_db_and_cleanup.function(file_names=file_names)


if __name__ == "__main__":
    main()
