"""statuses table

Revision ID: 8baec89c75f7
Revises: 9efd4f15f588
Create Date: 2023-04-20 13:17:31.311276

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "8baec89c75f7"
down_revision = "9efd4f15f588"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    with open("migrations/versions/statuses_table.sql", "r") as f:
        conn.execute(f.read())


def downgrade() -> None:
    op.execute(
        """
alter table osint."Attestation" drop column "txt";
    
ALTER TABLE osint."Attestation" DROP CONSTRAINT "Attestation_sigStatus_fkey";
ALTER TABLE osint."Attestation" DROP CONSTRAINT "Attestation_state_fkey";

drop table osint."EvidenceState";

drop TABLE osint."SignatureStatus";

CREATE TYPE osint."EvidenceState" AS ENUM (
    'created', -- presigned URL created to upload file, initial state
    'uploaded',
    'failed',
    'removed');

CREATE TYPE osint."SignatureStatus" AS ENUM (
    'in-progress',
    'verified',
    'unverified',
    'unsigned');
ALTER table osint."Attestation" ALTER COLUMN "sigStatus" TYPE osint."SignatureStatus" USING "sigStatus"::text::osint."SignatureStatus";
ALTER table osint."Attestation" ALTER COLUMN "state" SET DEFAULT 'created'::osint."EvidenceState";
ALTER table osint."Attestation" ALTER COLUMN "state" TYPE osint."EvidenceState" USING "state"::text::osint."EvidenceState";
alter table osint."Attestation" add column "txt" tsvector generated ALWAYS as
(to_tsvector('simple', "contentType" || ' ' || "contextType" || ' ' || context::text || ' ' ||
    coalesce(key, '') || ' ' ||
    coalesce(license, ''))) STORED;

    """
    )
