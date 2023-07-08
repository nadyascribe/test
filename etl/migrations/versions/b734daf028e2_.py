"""
Add statemenet-generic and attest-generic to ContentType 

Revision ID: b734daf028e2
Revises: 45ce892ef997
Create Date: 2023-06-06 14:23:17.838455

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "b734daf028e2"
down_revision = "45ce892ef997"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """INSERT INTO osint."ContentType" (enum, label) VALUES ('statemenet-generic', 'Generic Provenance'),
       ('attest-generic', 'Generic Provenance')"""
    )


def downgrade() -> None:
    op.execute(
        """DELETE FROM osint."Attestation" 
                  WHERE "contentType" IN ('statemenet-generic', 'attest-generic')"""
    )
    op.execute(
        """DELETE FROM osint."ContentType" 
                  WHERE (enum = 'statemenet-generic' AND label = 'Generic Provenance') OR 
                        (enum = 'attest-generic' AND label = 'Generic Provenance')"""
    )
