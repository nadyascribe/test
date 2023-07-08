alter table osint."Attestation" drop column "txt";

ALTER TABLE osint."Attestation" ALTER COLUMN "sigStatus" TYPE text;
ALTER TABLE osint."Attestation" ALTER COLUMN "state" TYPE text;
ALTER TABLE osint."Attestation" ALTER COLUMN "state" SET DEFAULT 'created';
DROP TYPE osint."SignatureStatus";
DROP TYPE osint."EvidenceState";
create table osint."EvidenceState" (
    enum  TEXT PRIMARY KEY
);

INSERT INTO osint."EvidenceState" (enum)
VALUES ('created'), -- presigned URL created to upload file, initial state
       ('uploaded'),
       ('failed'),
       ('removed');
CREATE TABLE osint."SignatureStatus" (
    enum  TEXT PRIMARY KEY
);
INSERT INTO osint."SignatureStatus" (enum)
VALUES ('in-progress'),
       ('verified'),
       ('unverified'),
       ('unsigned');
ALTER TABLE osint."Attestation" ADD CONSTRAINT "Attestation_sigStatus_fkey" FOREIGN KEY ("sigStatus") REFERENCES osint."SignatureStatus"(enum);

ALTER TABLE osint."Attestation" ADD CONSTRAINT "Attestation_state_fkey" FOREIGN KEY ("state") REFERENCES osint."EvidenceState"(enum);
alter table osint."Attestation" add column "txt" tsvector generated ALWAYS as
    (to_tsvector('simple', "contentType" || ' ' || "contextType" || ' ' || context::text || ' ' ||
                           coalesce(key, '') || ' ' || "sigStatus" || ' ' || state || ' ' ||
                           coalesce(license, ''))) STORED;