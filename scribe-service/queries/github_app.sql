-- name: DisableGithubInstallation :exec
UPDATE app."Team"
set "gitHubAppInstallationActive" = FALSE
WHERE "gitHubAppInstallationId" = @installation_id::bigint;

-- name: EnableGithubInstallation :exec
UPDATE app."Team"
set "gitHubAppInstallationActive" = TRUE
WHERE "gitHubAppInstallationId" = @installation_id::bigint;
