----------------------------------------------------------------
-- PipelineRun tables (ex. Build table)
----------------------------------------------------------------
CREATE SCHEMA IF NOT EXISTS osint;
DROP TABLE IF EXISTS osint."PipelineRun";
CREATE TABLE osint."PipelineRun"
(
    "id"           BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,

    "productKey"   TEXT   NOT NULL, -- ref Product.key: BaseHeader.NameField
    "pipelineName" TEXT   NOT NULL, -- context/workflow name: BaseHeader.PipelineName or BasePipelineHeader.workflow or ContextType
    "pipelineRun"  TEXT   NOT NULL, -- context/workflow run instance: BasePipelineHeader.RunID or ContextType + round_down(now(), 10mins)

    "context"      JSONB,           -- the workflow context from the attestation that created the build
    "version"      TEXT   NOT NULL, -- semver string: BaseHeader.Version or BaseSbomHeader.Version or timestampz string

    "timestamp"    TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    "team"         BIGINT NOT NULL, -- ref Team.id
    "publishedOn"  TIMESTAMPTZ,
    "deleted"      BOOLEAN     DEFAULT FALSE
);
CREATE INDEX "PipelineRun_product_idx" ON osint."PipelineRun" ("productKey");
CREATE INDEX "PipelineRun_version_idx" ON osint."PipelineRun" ("version");
CREATE INDEX "PipelineRun_timestamp_idx" ON osint."PipelineRun" ("timestamp");
CREATE INDEX "PipelineRun_team_idx" ON osint."PipelineRun" ("team");
CREATE INDEX "PipelineRun_publishedOn_idx" ON osint."PipelineRun" ("publishedOn");
CREATE INDEX "PipelineRun_pipelineName_idx" ON osint."PipelineRun" ("pipelineName");
CREATE INDEX "PipelineRun_pipelineRun_idx" ON osint."PipelineRun" ("pipelineRun");
CREATE INDEX "PipelineRun_deleted_idx" ON osint."PipelineRun" ("deleted");
----------------------------------------------------------------
-- Attestation tables 
----------------------------------------------------------------
DROP TABLE IF EXISTS osint."Attestation";
DROP TABLE IF EXISTS osint."ContentType";
DROP TABLE IF EXISTS osint."ContextType";
DROP TABLE IF EXISTS osint."TargetType";

CREATE TABLE osint."ContentType"
(
    enum  TEXT PRIMARY KEY,
    label TEXT,
    txt   tsvector generated always as ( to_tsvector('simple',
                                                     label
        ) ) stored -- full-text search
);
INSERT INTO osint."ContentType" (enum, label)
VALUES ('cyclonedx-json', 'SBOM CycloneDX'),
       ('attest-cyclonedx-json', 'SBOM CycloneDX'),
       ('statement-cyclonedx-json', 'SBOM CycloneDX'),
       ('attest-slsa', 'SLSA Provenance'),
       ('statement-slsa', 'SLSA Provenance'),
       ('ssdf', 'SSDF evidence'),
       ('scorecard', 'Package Scorecard'),
       ('policy-run', 'Policy evaluation');

CREATE TABLE osint."ContextType"
(
    enum  TEXT PRIMARY KEY,
    label TEXT,
    txt   tsvector generated always as ( to_tsvector('simple',
                                                     label
        ) ) stored -- full-text search
);
INSERT INTO osint."ContextType" (enum, label)
VALUES ('other', 'Other'),
       ('local', 'Local build'),
       ('jenkins', 'Jenkins'),
       ('github', 'GitHub Workflow'),
       ('circleci', 'CircleCI'),
       ('azure', 'Azure Devops'),
       ('gitlab', 'Gitlab'),
       ('travis', 'Travis'),
       ('bitbucket', 'Bitbucket'),
       ('scorecard', 'OSSF Scorecard'),
       ('githubapp', 'GitHub App'),
       ('scribe', 'Scribe Service');

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

CREATE TABLE osint."TargetType"
(
    enum  TEXT PRIMARY KEY,
    label TEXT,
    txt   tsvector generated always as ( to_tsvector('simple',
                                                     label
        ) ) stored -- full-text search
);
INSERT INTO osint."TargetType" (enum, label)
VALUES ('other', 'Other'),
       ('image', 'Image'),
       ('directory', 'Folder'),
       ('file', 'File'),
       ('git', 'Git repo'),
       ('github-account', 'GitHub Account');

CREATE TABLE osint."Attestation"
(
    "id"          BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    "contentType" TEXT                  NOT NULL REFERENCES osint."ContentType" (enum),
    "targetType"  TEXT                  NOT NULL REFERENCES osint."TargetType" (enum),
    "targetName"  TEXT                  NOT NULL,                                     -- sbom name, purl, image name, or something  --<<new
    "contextType" TEXT                  NOT NULL REFERENCES osint."ContextType" (enum),
    "context"     JSONB                 NOT NULL,                                     -- context of the attestation
    "key"         TEXT,                                                               -- S3 URI
    "timestamp"   TIMESTAMPTZ                    DEFAULT CURRENT_TIMESTAMP,
    "userId"      BIGINT,                                                             -- ref app.User.id,
    "teamId"      BIGINT                         DEFAULT 0,                           -- ref app.Team.id" -- makes attestation private
    "pipelineRun" BIGINT                NOT NULL REFERENCES osint."PipelineRun" (id), --
    "state"       osint."EvidenceState" not null DEFAULT 'created',
    "sigStatus"   osint."SignatureStatus",
    "alerted"     BOOLEAN                        DEFAULT FALSE,
    "license"     TEXT,
    "deleted"     BOOLEAN                        DEFAULT FALSE,
    "txt"         tsvector GENERATED ALWAYS AS
                      (to_tsvector('simple', "contentType" || ' ' || "contextType" || ' ' || context::text || ' ' ||
                                             coalesce(key, '') || ' ' ||
                                             coalesce(license, ''))) STORED,          -- full-text search
    job_ids       text[]                not null default '{}',                        -- airflow run_id
    project       text                  null GENERATED ALWAYS AS (context ->> 'git_url') STORED
);

CREATE INDEX "Attestation_contentType_key" ON osint."Attestation" ("contentType");
CREATE INDEX "Attestation_contextType_key" ON osint."Attestation" ("contextType");
CREATE INDEX "Attestation_targetType_key" ON osint."Attestation" ("targetType");
CREATE INDEX "Attestation_targetName_key" ON osint."Attestation" ("targetName");
CREATE INDEX "Attestation_context_key" ON osint."Attestation" USING GIN ("context");
CREATE INDEX "Attestation_timestamp_key" ON osint."Attestation" ("timestamp");
CREATE INDEX "Attestation_userId_key" ON osint."Attestation" ("userId");
CREATE INDEX "Attestation_teamId_key" ON osint."Attestation" ("teamId");
CREATE INDEX "Attestation_pipelineRun_key" ON osint."Attestation" ("pipelineRun");
CREATE INDEX "Attestation_state_key" ON osint."Attestation" ("state");
CREATE INDEX "Attestation_license_key" ON osint."Attestation" ("license");
CREATE INDEX "Attestation_deleted_key" ON osint."Attestation" ("deleted");
CREATE INDEX "Attestation_txt_key" ON osint."Attestation" USING GIN ("txt");

----------------------------------------------------------------
-- Component tables
----------------------------------------------------------------
DROP TABLE IF EXISTS osint."AttestationComponent";
DROP TABLE IF EXISTS osint."Component";
DROP TABLE IF EXISTS osint."ComponentType";
CREATE TABLE osint."ComponentType"
(
    enum  TEXT PRIMARY KEY,
    label TEXT,
    txt   tsvector generated always as ( to_tsvector('simple',
                                                     label
        ) ) stored -- full-text search
);
INSERT INTO osint."ComponentType" (enum, label)
VALUES -- list from cyclonedx spec:
       ('unknown', 'Unknown package'),
       ('binary', 'Binary'),
       ('apk', 'Android APK'),
       ('alpm', 'ArchLinux package'),
       ('gem', 'Ruby Gem'),
       ('deb', 'Debian package'),
       ('rpm', 'Redhat package'),
       ('npm', 'Node package'),
       ('python', 'Python package'),
       ('php-composer', 'PHP package'),
       ('java-archive', 'Java archive'),
       ('jenkins-plugin', 'Jenkins plugin'),
       ('go-module', 'Go module'),
       ('rust-crate', 'Rust crate'),
       ('msrc-kb', 'SolarWinds MSRC/KB'),
       ('dart-pub', 'Dart publish'),
       ('dotnet', 'Dotnet NUGET'),
       ('pod', 'Pod package'),
       ('conan', 'C++ Conan package'),
       ('portage', 'Gentoo Linux package Portage'),
       ('hackage', 'Haskell package Hackage'),
       -- list of other known types:
       ('base-image', 'Base image'),
       ('container', 'Container image'),
       ('tar', 'Tar archive'),
       ('wmi', 'WMI package'),
       ('layer', 'Layer image'),
       ('file', 'File'),
       ('syft', 'Syft package'),
       ('zip', 'Compressed archive ZIP');
CREATE TABLE osint."Component"
(
    "id"              BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    "purl"            TEXT   NOT NULL,
    "teamId"          BIGINT NOT NULL DEFAULT 0,                                    -- ref app.Team.id" makes component private
    "type"            TEXT,
    "group"           TEXT   NOT NULL REFERENCES osint."ComponentType" (enum) ON DELETE CASCADE,
    -- ex. layer, commit, file, dependency etc.
    "cpes"            TEXT[] NOT NULL,
    "name"            TEXT   NOT NULL,
    "mainAttestation" BIGINT REFERENCES osint."Attestation" (id) ON DELETE CASCADE, -- the main attestation describing this component, used for child components
    "info"            JSONB,-- relevant info from related attestation/s
    "extraIdx"        BIGINT[],-- optional; ref osint.Attestation.id
    "licenses"        JSONB,
    "txt"             tsvector GENERATED ALWAYS AS (
                          to_tsvector('simple',
                                      purl || ' ' || name || ' ' || coalesce(info, '{}')::text || ' ' ||
                                      coalesce(licenses, '[]')::text
                              )
                          ) STORED,                                                 -- full-text search
    "version"         text   null GENERATED ALWAYS AS (info ->> 'version') STORED
);
CREATE INDEX "Component_type_key" ON osint."Component" ("type");
CREATE UNIQUE INDEX "Component_purl_teamId_key" ON osint."Component" ("purl", "teamId");
CREATE INDEX "Component_group_key" ON osint."Component" ("group");
CREATE INDEX "Component_cpes_key" ON osint."Component" USING GIN ("cpes");
CREATE INDEX "Component_name_key" ON osint."Component" ("name");
CREATE INDEX "Component_attestation_key" ON osint."Component" ("mainAttestation");
CREATE INDEX "Component_license_key" ON osint."Component" USING GIN ("licenses"); -- gin ?????
CREATE INDEX "Component_txt_key" ON osint."Component" USING GIN ("txt");
-- Add full-text search on other fields

-- child components for the attestation
CREATE TABLE osint."AttestationComponent"
(
    attestation BIGINT REFERENCES osint."Attestation" (id),
    component   BIGINT REFERENCES osint."Component" (id),
    PRIMARY KEY (attestation, component),
    info        JSONB -- list of importer_path, later_ref objects etc.
);
CREATE INDEX "AttestationComponent_component_key" ON osint."AttestationComponent" ("component");
----------------------------------------------------------------
-- Vulnerability table 
----------------------------------------------------------------
DROP TABLE IF EXISTS osint."VulComponent";
DROP TABLE IF EXISTS osint."Vulnerability";
CREATE TABLE osint."Vulnerability"
(
    "id"              TEXT PRIMARY KEY,
    "publishedOn"     TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    "lastModified"    TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    "severity"        REAL,    -- from grype report; map to severity strings in app level
    "cvssScore"       REAL,    -- latest related VulAdvisory.info.cvss.baseScore
    "epssProbability" REAL,    -- latest related VulAdvisory.info.epss.probability
    "txt"             tsvector generated always as ( to_tsvector('simple',
                                                                 id
        ) ) stored          -- full-text search
);
CREATE INDEX "Vulnerability_publishedOn_key" ON osint."Vulnerability" ("publishedOn");
CREATE INDEX "Vulnerability_lastModified_key" ON osint."Vulnerability" ("lastModified");

CREATE INDEX "Vulnerability_severity_key" ON osint."Vulnerability" ("severity");
CREATE INDEX "Vulnerability_cvssScore_key" ON osint."Vulnerability" ("cvssScore");
CREATE INDEX "Vulnerability_epssProbability_key" ON osint."Vulnerability" ("epssProbability");
CREATE INDEX "Vulnerability_txt_key" ON osint."Vulnerability" USING GIN ("txt");
-- Add full-text search on other fields

-- list of components per vulnarability --<<new table
CREATE TABLE osint."VulComponent"
(
    "component"      BIGINT REFERENCES osint."Component" ("id"),
    "vulId"          TEXT REFERENCES osint."Vulnerability" (id), -- CVE string
    PRIMARY KEY ("component", "vulId"),
    "fixedInVersion" TEXT                                        -- text from Grype report
);

----------------------------------------------------------------
-- Vulnerability Advisory table 
----------------------------------------------------------------
DROP TABLE IF EXISTS osint."VulAdvisory";
DROP TABLE IF EXISTS osint."AdvisoryType";

CREATE TABLE osint."AdvisoryType"
(
    enum TEXT PRIMARY KEY
);
INSERT INTO osint."AdvisoryType" (enum)
VALUES ('NVD3.1'),
       ('NVD3'),
       ('NVD2'),
       ('OSV');

CREATE TABLE osint."VulAdvisory"
(
    "id"           BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    "vulId"        TEXT   NOT NULL REFERENCES osint."Vulnerability" (id), -- CVE string
    "source"       TEXT   NOT NULL REFERENCES osint."AdvisoryType" (enum),
    "lastModified" TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    "vector"       TEXT,
    "cpes"         TEXT[] NOT NULL,
    -- affected components; partial match on Component.cpes
    "publishedOn"  TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
    "hyperLinks"   TEXT[],
    "baseScore"    REAL,
    -- baseScore of newest cvss
    "advisoryText" TEXT,
    "info"         JSONB                                                  -- ex. epss { probability }, cvss { baseScore, impactScore, exploitabilityScore }
);

-- primary key enforces all fields to be not null. therefore we have to create unique index because lastModified can be null.
CREATE UNIQUE INDEX "VulAdvisory_vulId_source_lastModified" ON osint."VulAdvisory" ("vulId", "source", "lastModified");
CREATE INDEX "VulAdvisory_vulId_key" ON osint."VulAdvisory" ("vulId");
CREATE INDEX "VulAdvisory_source_key" ON osint."VulAdvisory" ("source");
CREATE INDEX "VulAdvisory_lastModified_key" ON osint."VulAdvisory" ("lastModified");

DROP TABLE IF EXISTS osint."PipelineAttestation";
DROP TABLE IF EXISTS osint."PipelineAdvisory";

----------------------------------------------------------------
-- ComplianceRule tables
----------------------------------------------------------------
DROP TABLE IF EXISTS osint."ComplianceRule";
DROP TABLE IF EXISTS osint."ComplianceType";

CREATE TABLE osint."ComplianceType"
(
    enum TEXT PRIMARY KEY
);
INSERT INTO osint."ComplianceType" (enum)
VALUES ('SLSA'),
       ('SSDF');

CREATE TABLE osint."ComplianceRule"
(
    "id"                   BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    "type"                 TEXT NOT NULL REFERENCES osint."ComplianceType" (enum),
    "ruleName"             TEXT NOT NULL,
    "ruleId"               TEXT,
    "description"          TEXT, -- short description
    "messagePass"          TEXT,
    "messageFail"          TEXT,
    "messageReview"        TEXT,
    "messageOpen"          TEXT,
    "messageInformational" TEXT,
    "messageNotApplicable" TEXT,
    "slsaLevel"            INT,
    "txt"                  tsvector generated always as ( to_tsvector('simple',
                                                                      "ruleName" || ' ' || description || ' ' || "type"
        ) ) stored-- full-text search
);
CREATE INDEX "ComplianceRule_txt_key" ON osint."ComplianceRule" USING GIN ("txt");
CREATE INDEX "ComplianceRule_type_idx" on osint."ComplianceRule" ("type");
----------------------------------------------------------------
-- ComplianceRun tables
----------------------------------------------------------------
DROP TABLE IF EXISTS osint."ComplianceRun";
DROP TABLE IF EXISTS osint."ComplianceStatus";

CREATE TABLE osint."ComplianceStatus"
(
    enum  TEXT PRIMARY KEY,
    label TEXT,
    txt   tsvector generated always as ( to_tsvector('simple',
                                                     label
        ) ) stored -- full-text search
);
INSERT INTO osint."ComplianceStatus" (enum, label)
VALUES ('pass', 'Passed'),
       ('fail', 'Failed'),
       ('review', 'In review'),
       ('open', 'Open'),
       ('informational', 'Information'),
       ('not-applicable', 'Not applicable');

CREATE TABLE osint."ComplianceRun"
(
    "id"          BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    "pipelineRun" BIGINT NOT NULL REFERENCES osint."PipelineRun" (id),
    "rule"        BIGINT NOT NULL REFERENCES osint."ComplianceRule" (id),
    "status"      TEXT   NOT NULL REFERENCES osint."ComplianceStatus" (enum),
    "message"     TEXT DEFAULT '',
    "txt"         tsvector generated always as ( to_tsvector('simple',
                                                             status || ' ' || message
        ) ) stored-- full-text search
);

CREATE INDEX "ComplianceRun_pipeline_idx" on osint."ComplianceRun" ("pipelineRun");
CREATE INDEX "ComplianceRun_status_idx" on osint."ComplianceRun" ("status");
CREATE INDEX "ComplianceRun_message_idx" on osint."ComplianceRun" ("message");
CREATE INDEX "ComplianceRun_txt_key" ON osint."ComplianceRun" USING GIN ("txt");
