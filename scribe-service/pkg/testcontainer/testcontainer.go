package testcontainer

import (
	"context"
	"fmt"

	"github.com/docker/go-connections/nat"
	"github.com/jmoiron/sqlx"
	"github.com/testcontainers/testcontainers-go"
	"github.com/testcontainers/testcontainers-go/wait"

	"github.com/scribe-security/scribe2/scribe-service/pkg/config"
	"github.com/scribe-security/scribe2/scribe-service/pkg/connection"
	"github.com/scribe-security/scribe2/scribe-service/pkg/helpers"
)

// CreateTestContainer with database for tests
func CreateTestContainer(ctx context.Context, dbname string) (testcontainers.Container, *sqlx.DB, error) {
	network := helpers.GetEnv("DOCKER_NETWORK", "mono")
	env := map[string]string{
		"POSTGRES_PASSWORD": "postgres",
		"POSTGRES_USER":     "postgres",
		"POSTGRES_DB":       dbname,
	}
	port := "5432/tcp"
	req := testcontainers.GenericContainerRequest{
		ContainerRequest: testcontainers.ContainerRequest{
			Image:        "postgres:13.4-alpine",
			ExposedPorts: []string{port},

			// TODO: use network name from env.
			// TODO: generate new name as network alias
			Networks:       []string{network},
			NetworkAliases: map[string][]string{network: {"test"}},
			Env:            env,
			WaitingFor:     wait.ForListeningPort(nat.Port(port)), // wait.ForLog("database system is ready to accept connections"),

		},
		Started: true,
	}

	container, err := testcontainers.GenericContainer(ctx, req)
	if err != nil {
		return container, nil, fmt.Errorf("start container: %w", err)
	}

	containerHost, err := container.Host(ctx)
	if err != nil {
		return nil, nil, fmt.Errorf("get container host name: %w", err)
	}

	localPort, err := container.MappedPort(ctx, "5432")
	if err != nil {
		return nil, nil, fmt.Errorf("get local mapped port: %w", err)
	}

	db := connection.NewPostgres(ctx, config.Postgres{
		User:     "postgres",
		Password: "postgres",
		Host:     containerHost,
		Port:     localPort.Int(),
		DB:       dbname,
	}.String())

	return container, db, nil
}

// CreateTestContainer with database for tests
func CreateLocalstackTestContainer(ctx context.Context) (testcontainers.Container, string, error) {
	network := helpers.GetEnv("DOCKER_NETWORK", "mono")
	env := map[string]string{
		"SERVICES":              "s3",
		"LAMBDA_DOCKER_NETWORK": network,
		"REQUIRE_PRO":           "0",
	}
	port := "4566"
	req := testcontainers.GenericContainerRequest{
		ContainerRequest: testcontainers.ContainerRequest{
			Image:        "localstack/localstack:latest",
			ExposedPorts: []string{port},

			// TODO: use network name from env.
			// TODO: generate new name as network alias
			Networks:       []string{network},
			NetworkAliases: map[string][]string{network: {"test"}},
			Env:            env,
			WaitingFor:     wait.ForExec([]string{"awslocal", "s3", "ls"}),
		},
		Started: true,
	}

	container, err := testcontainers.GenericContainer(ctx, req)
	if err != nil {
		return container, "", fmt.Errorf("start container: %w", err)
	}

	containerHost, err := container.Host(ctx)
	if err != nil {
		return nil, "", fmt.Errorf("get container host name: %w", err)
	}

	localPort, err := container.MappedPort(ctx, nat.Port(port))
	if err != nil {
		return nil, "", fmt.Errorf("get local mapped port: %w", err)
	}

	endpoint := fmt.Sprintf("http://%v:%v", containerHost, localPort.Port())

	return container, endpoint, nil
}

// CreateTestContainer with redis and async for tests

func CreateRedisAsyncTestContainer(ctx context.Context) (testcontainers.Container, string, error) {
	network := helpers.GetEnv("DOCKER_NETWORK", "mono")

	port := "6379/tcp"
	req := testcontainers.GenericContainerRequest{
		ContainerRequest: testcontainers.ContainerRequest{
			Image:        "redislabs/rejson",
			ExposedPorts: []string{port},

			// TODO: use network name from env.
			// TODO: generate new name as network alias
			Networks:       []string{network},
			NetworkAliases: map[string][]string{network: {"test"}},
			Env:            nil,
			WaitingFor:     wait.ForListeningPort(nat.Port(port)), // wait.ForLog("database system is ready to accept connections"),

		},
		Started: true,
	}

	container, err := testcontainers.GenericContainer(ctx, req)
	if err != nil {
		return container, "", fmt.Errorf("start container: %w", err)
	}

	containerHost, err := container.Host(ctx)
	if err != nil {
		return nil, "", fmt.Errorf("get container host name: %w", err)
	}

	localPort, err := container.MappedPort(ctx, "6379")
	if err != nil {
		return nil, "", fmt.Errorf("get local mapped port: %w", err)
	}

	addr := fmt.Sprintf("%s:%s", containerHost, localPort.Port())

	return container, addr, nil
}
