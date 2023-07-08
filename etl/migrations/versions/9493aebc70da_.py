"""

Revision ID: 9493aebc70da
Revises: c98760297aa9
Create Date: 2023-05-10 07:57:20.810628

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "9493aebc70da"
down_revision = "c98760297aa9"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "vul_advisory",
        sa.Column(
            "txt",
            postgresql.TSVECTOR(),
            sa.Computed(
                "to_tsvector('simple', \"source\" || ' ' || coalesce(\"advisoryText\", ''))",
                persisted=True,
            ),
            nullable=True,
        ),
        schema="osint",
    )


def downgrade() -> None:
    op.drop_column("vul_advisory", "txt", schema="osint")
