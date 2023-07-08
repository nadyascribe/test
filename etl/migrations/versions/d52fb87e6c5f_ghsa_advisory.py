"""ghsa advisory

Revision ID: d52fb87e6c5f
Revises: f9475afcf639
Create Date: 2023-05-24 09:43:59.719078

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "d52fb87e6c5f"
down_revision = "f9475afcf639"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("""INSERT INTO osint."AdvisoryType" (enum) VALUES ('GHSA')""")


def downgrade() -> None:
    op.execute("""DELETE FROM osint."AdvisoryType" where enum = 'GHSA'""")
