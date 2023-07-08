
-- name: CreateEvidence :one
INSERT INTO osint."Attestation" (
    "key",
    "teamId",
    "contentType",
    "contextType",
    "context",
    "pipelineRun",
    "targetType",
    "targetName",
    "logical_app",
    "logical_app_version",
    "tool"
) VALUES (
    @key,
    @teamId::BIGINT,
    @contentType::TEXT,
    @contextType::TEXT,
    @context::jsonb,
    @pipelineRun::BIGINT,
    @targetType::TEXT,
    @targetName::TEXT,
    --these fields may be null so don't cast to text
    @logicalApp,
    @logicalAppVersion,
    @tool
)
RETURNING *;

-- name: GetEvidenceByKey :one
SELECT
    *
FROM
    osint."Attestation"
WHERE
    key = $1;

-- name: GetEvidenceByFileID :one
SELECT
    *
FROM
    osint."Attestation"
WHERE
    id = $1;

-- name: SetEvidenceState :exec
UPDATE
    osint."Attestation"
SET
    state = @state
WHERE
    id = @id::BIGINT;

-- name: DeleteEvidence :exec
DELETE FROM osint."Attestation"
WHERE
    "teamId" = @teamId::BIGINT AND
    CASE WHEN @id::BIGINT > 0 THEN
        id = @id::BIGINT
    ELSE
        CASE WHEN @key::TEXT <> '' THEN
            CASE WHEN strpos(@key::TEXT, '%') > 0 THEN
                key LIKE @key::TEXT
            ELSE
                key = @key::TEXT
            END
        ELSE
            TRUE
        END
    END;


-- name: UpdateContext :exec
UPDATE
    osint."Attestation"
SET
    context = @context::JSONB
WHERE
    id = @id::BIGINT;


-- name: ListEvidence :many
SELECT
    "id",
    "contentType",
    "contextType",
    "context" ,
    "key",    -- S3 URI
    "timestamp" ,
    "userId",  -- ref osint.User.id,
    "teamId",  -- ref osint.Team.id" -- makes attestation private
    "license",
    "txt", -- full-text search
    "state"
FROM
    osint."Attestation"
WHERE
    (@input::jsonb <@context::jsonb) AND
    (@teamId::BIGINT = "teamId"); -- note: this may be vulnerable to JSON injection, sanitize user input in code
