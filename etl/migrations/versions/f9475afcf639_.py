"""

Revision ID: f9475afcf639
Revises: b4863702e0e3
Create Date: 2023-05-22 15:47:13.501044

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "f9475afcf639"
down_revision = "b4863702e0e3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "ComplianceRun",
        sa.Column("info", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        schema="osint",
    )
    op.execute("""INSERT INTO osint."ComplianceType" (enum) VALUES ('GitIntegrity')""")
    op.execute(
        """
        INSERT INTO osint."ComplianceRule" ("type", "ruleName") 
        VALUES ('GitIntegrity', 'Git Integrity Rule');
        """
    )


def downgrade() -> None:
    op.drop_column("ComplianceRun", "info", schema="osint")
    op.execute("""DELETE FROM osint."ComplianceRule" WHERE "type" = 'GitIntegrity'""")
    op.execute("""DELETE FROM osint."ComplianceType" WHERE enum = 'GitIntegrity'""")
