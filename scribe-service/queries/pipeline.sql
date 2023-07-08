-- name: CreatePipelineRun :one
INSERT INTO osint."PipelineRun" (
    "productKey",
    "pipelineName",
    "pipelineRun",
    "context",
    "version",
    "team"
) VALUES (
    @productKey::TEXT,
    @pipelineName::TEXT,
    @pipelineRun::TEXT,
    @context::JSONB,
    @version::TEXT,
    @team::BIGINT
)
RETURNING *;

-- name: GetPipelineRun :one
SELECT
    *
FROM
    osint."PipelineRun"
WHERE
    @productKey::TEXT = "productKey" AND
    @pipelineName::TEXT = "pipelineName" AND
    @pipelineRun::TEXT = "pipelineRun" AND
    @team::BIGINT = team;


-- name: GetPipelineRunByGitURL :one
SELECT
    *
FROM
    osint."PipelineRun"
WHERE
    (context ->> 'git_url') = ANY(@gitUrls::TEXT[])
ORDER BY id DESC LIMIT 1;