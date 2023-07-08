"""

Revision ID: c98760297aa9
Revises: 02fbae7ac490
Create Date: 2023-05-10 06:39:55.174066

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "c98760297aa9"
down_revision = "02fbae7ac490"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.rename_table("VulAdvisory", "vul_advisory", "osint")
    op.alter_column("vul_advisory", "vulId", new_column_name="vul_id", schema="osint")


def downgrade() -> None:
    op.rename_table("vul_advisory", "VulAdvisory", "osint")
    op.alter_column("VulAdvisory", "vul_id", new_column_name="vulId", schema="osint")
