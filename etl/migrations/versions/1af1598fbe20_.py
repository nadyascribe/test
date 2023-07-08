"""

Revision ID: 1af1598fbe20
Revises: 109987869046
Create Date: 2023-05-16 08:58:29.960657

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "1af1598fbe20"
down_revision = "109987869046"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute('ALTER TABLE osint."Attestation" ALTER COLUMN "sigStatus" SET DEFAULT \'in-progress\';')


def downgrade() -> None:
    op.execute('ALTER TABLE osint."Attestation" ALTER COLUMN "sigStatus" DROP DEFAULT;')
