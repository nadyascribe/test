"""

Revision ID: a5d493e4b470
Revises: d52fb87e6c5f
Create Date: 2023-05-24 16:04:20.063659

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "a5d493e4b470"
down_revision = "d52fb87e6c5f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "ComplianceRun",
        sa.Column("attestations", sa.ARRAY(sa.BigInteger()), nullable=True),
        schema="osint",
    )


def downgrade() -> None:
    op.drop_column("ComplianceRun", "attestations", schema="osint")
