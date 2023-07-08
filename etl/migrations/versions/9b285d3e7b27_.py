"""

Revision ID: 9b285d3e7b27
Revises: 1af1598fbe20
Create Date: 2023-05-16 12:18:07.682252

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "9b285d3e7b27"
down_revision = "1af1598fbe20"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute('ALTER TABLE osint."PipelineRun" DROP COLUMN "publishedOn";')


def downgrade() -> None:
    op.execute('ALTER TABLE osint."PipelineRun" ADD COLUMN "publishedOn" TIMESTAMPTZ;')
