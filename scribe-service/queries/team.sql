-- name: GetTeamIDByName :one
SELECT
    *
FROM
    app."Team"
WHERE
    @teamName::TEXT = name;


-- name: GetTeamByClientID :one
SELECT
    *
FROM
    app."Team"
WHERE
    "clientId" = $1;
