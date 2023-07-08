-- name: CreateProduct :one
INSERT INTO app."Product" (
    "name",
    "teamId",
    "key",
    "userDefinedKey")
VALUES (
    @name::TEXT,
    @teamId::BIGINT,
    @key::TEXT,
    @userDefinedKey::TEXT
)
RETURNING *;


-- name: GetProduct :one
SELECT 
    * 
FROM 
    app."Product"
WHERE 
    "userDefinedKey" = @userDefinedKey::TEXT AND "teamId" = @teamId::BIGINT;