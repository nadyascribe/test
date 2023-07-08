"""

Fix generic content type spelling, add target type

Revision ID: 40b5d31652ac
Revises: b734daf028e2
Create Date: 2023-06-07 13:57:14.109926

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "40b5d31652ac"
down_revision = "b734daf028e2"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # remove the type
    op.execute(
        """DELETE FROM osint."Attestation" 
                  WHERE "contentType"='statemenet-generic'"""
    )
    op.execute(
        """DELETE FROM osint."ContentType" 
                  WHERE (enum = 'statemenet-generic' AND label = 'Generic Provenance')"""
    )

    # add the correct spelling
    op.execute("""INSERT INTO osint."ContentType" (enum, label) VALUES ('statement-generic', 'Generic Provenance')""")


def downgrade() -> None:
    # remove the new spelling
    op.execute(
        """DELETE FROM osint."Attestation" 
                  WHERE "contentType"='statement-generic'"""
    )
    op.execute(
        """DELETE FROM osint."ContentType" 
                  WHERE (enum = 'statement-generic' AND label = 'Generic Provenance')"""
    )

    # add the old spelling
    op.execute("""INSERT INTO osint."ContentType" (enum, label) VALUES ('statemenet-generic', 'Generic Provenance')""")
