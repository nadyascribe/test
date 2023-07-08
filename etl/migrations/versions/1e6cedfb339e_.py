"""

Revision ID: 1e6cedfb339e
Revises: d52fb87e6c5f
Create Date: 2023-05-28 06:47:43.548580

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = "1e6cedfb339e"
down_revision = "a5d493e4b470"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
    alter table osint."Attestation" drop column "project";
    alter table osint."Attestation" add column project text generated always as ((context ->> 'git_url'::text)) stored;
    alter table osint."Vulnerability" alter column severity type integer;
    alter table osint."Vulnerability" alter column severity set not null;
    alter table osint."Vulnerability" drop column txt;
    alter table osint."Vulnerability" add column txt text generated always 
            as (to_tsvector('simple'::regconfig,
                (((((id || ' '::text) || replace(id, '-'::text, ' '::text)) ||
                ' '::text) || COALESCE(("cvssScore")::text, ''::text)) ||
                 COALESCE(
                 (round(("epssProbability" * (100)::double precision)))::text,
                 ''::text)))) stored;
    alter table osint."VulComponent" drop column if exists txt;
    alter table osint."VulComponent" add column txt text generated always 
            as (to_tsvector('simple'::regconfig, "fixedInVersion")) stored;
    """
    )


def downgrade() -> None:
    op.execute(
        """
alter table osint."Vulnerability" alter column severity type real;
    alter table osint."Vulnerability" alter column severity drop not null;
    alter table osint."VulComponent" drop column txt;
    """
    )
