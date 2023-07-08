"""init

Revision ID: b98e20345719
Revises: 
Create Date: 2023-03-05 12:20:35.061579

"""
import pandas as pd
from alembic import context, op
from sqlalchemy.engine.mock import MockConnection

# revision identifiers, used by Alembic.
revision = "b98e20345719"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    with open("migrations/versions/init.sql", "r") as f:
        conn.execute(f.read())
    # if we are generating raw sql, we don't want to load the data
    if not isinstance(conn, MockConnection):
        df = pd.read_csv(
            "migrations/Licenses.csv",
            header=0,
            sep=",",
            quotechar='"',
            error_bad_lines=False,
        )
        df.to_sql(name="licenses", con=conn, if_exists="replace", index=False, chunksize=10000)

    args = context.get_x_argument(as_dictionary=True)
    if args.get("with-seed", False):
        _data_upgrades(conn)


def downgrade() -> None:
    conn = op.get_bind()
    with open("migrations/versions/init.sql", "r") as f:
        for l in f.readlines():
            l = l.replace("IF NOT EXISTS ", "")
            if "create table" in l.lower():
                print("dropping table " + l.split(" ")[2].strip())
                conn.execute("drop table if exists " + l.split(" ")[2] + " cascade;")
            if "create type" in l.lower():
                print("dropping type " + l.split(" ")[2].strip())
                conn.execute("drop type if exists " + l.split(" ")[2] + " cascade;")


def _data_upgrades(conn):
    print("perform data upgrades")
    # if we put it into downgrade function then we have to handle the same --with-seed argument for downgrades
    conn.execute("drop schema if exists app cascade")
    with open("migrations/versions/temp_app.sql", "r") as f:
        conn.execute(f.read())
    with open("migrations/versions/initial_seed.sql", "r") as f:
        conn.execute(f.read())
