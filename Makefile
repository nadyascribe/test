.PHONY: all

VERSION = $(shell git describe --always --tags --dirty)
VERSION_LDFLAGS = "-X=github.com/scribe-security/etl-flows/etl/internal/version.version=$(VERSION)"
GO_BINARY=scribe-service
DOCKER_COMPOSE_FILE=etl/docker-compose.yml
GIT_BRANCH = $(shell git rev-parse --abbrev-ref HEAD)
GITHUB_REPO_NAME = "scribe-security/scribe2"

TEMPDIR = .tmp
SWAGGER_GENERATED_DIR_NAME = genclient
SWAGGER_GENERATED_DIR = $(TEMPDIR)/$(SWAGGER_GENERATED_DIR_NAME)
SWAGGER_CONFIG = scribe-api.yaml

.PHONY: help
help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(BOLD)$(CYAN)%-25s$(RESET)%s\n", $$1, $$2}'

SWAGGER = docker run --rm -it \
			--user $(shell id -u):$(shell id -g) \
			-e GOPATH=${HOME}/go:/go \
			-e DEBUG=true \
			-e XDG_CACHE_HOME=${HOME}/.cache \
			-v ${HOME}:${HOME} \
			-w $(shell pwd)/scribe-service quay.io/goswagger/swagger

ifneq (,$(wildcard ./etl/.env_local))
    include ./etl/.env_local
    export
endif

# we can't put it inside of Dockerfile because the command requires initialized airflow database
import-airflow-vars:
	docker compose -f $(DOCKER_COMPOSE_FILE) cp etl/vars.json webserver:/vars.json
	docker compose -f $(DOCKER_COMPOSE_FILE) cp etl/conns.json webserver:/conns.json
	docker compose -f $(DOCKER_COMPOSE_FILE) exec -u airflow webserver airflow variables import /vars.json
	docker compose -f $(DOCKER_COMPOSE_FILE) exec -u airflow webserver airflow connections import /conns.json

start-airflow-local:
	docker compose -f $(DOCKER_COMPOSE_FILE) build
	docker compose -f $(DOCKER_COMPOSE_FILE) up -d

erase-airflow-local:
	docker compose -f $(DOCKER_COMPOSE_FILE) down -v

persist-data-local:
	(cd etl && python scripts/local_minio_data.py)
	docker compose -f $(DOCKER_COMPOSE_FILE) run --rm createbuckets

init-airflow-local: start-airflow-local import-airflow-vars migration-up

stop-airflow-local:
	docker compose -f $(DOCKER_COMPOSE_FILE) stop

lint-go: format-go
	(cd scribe-service && golangci-lint -vv run)

format-go:
	(cd scribe-service && go fmt ./...)
	gci write --skip-generated -s "standard,default,prefix(github.com/scribe-security/scribe)" scribe-service/

lint-py: format-py
	(cd etl && pylama)

mypy:
	(cd etl && mypy dags)

format-py:
	black --version
	(cd etl && black . && autoflake --quiet dags)

lint-all: lint-go lint-py

migration-up:
	# `-x with-seed=true` only for local development
	docker compose -f $(DOCKER_COMPOSE_FILE) exec -u airflow webserver alembic -x with-seed=true upgrade head

migration-sql:
	docker compose -f $(DOCKER_COMPOSE_FILE) exec -u airflow webserver alembic -x pure-output=true upgrade --sql head

migration-down:
	docker compose -f $(DOCKER_COMPOSE_FILE) exec -u airflow webserver alembic downgrade -1

migration-erase:
	docker compose -f $(DOCKER_COMPOSE_FILE) exec -u airflow webserver alembic downgrade base

migration-new:
	# must be run using root user, otherwise PermissionError raises
	docker compose -f $(DOCKER_COMPOSE_FILE) exec webserver /bin/bash -c "PYTHONPATH=/home/airflow/.local/lib/python3.10/site-packages alembic revision -m '$(name)'"
	# owner of the file is root, so we need to change it to the current user
	docker compose -f $(DOCKER_COMPOSE_FILE) exec webserver chown -R $(shell id -u):$(shell id -u) /opt/airflow/migrations

migration-new-auto:
	# must be run using root user, otherwise PermissionError raises
	docker compose -f $(DOCKER_COMPOSE_FILE) exec webserver /bin/bash -c "PYTHONPATH=/home/airflow/.local/lib/python3.10/site-packages alembic revision --autogenerate -m '$(name)'"
	# owner of the file is root, so we need to change it to the current user
	docker compose -f $(DOCKER_COMPOSE_FILE) exec webserver chown -R $(shell id -u):$(shell id -u) /opt/airflow/migrations

tests-py:
	# required to have postgres running
	(cd etl && pytest --cov=dags --cov-report html -v tests/integrations)

serve: ## run server under air control with reloading
	SCRIBE_CONFIG_PATH=scribe-service/configs air -d -c scribe-service/.air.conf

build: go-dependencies build-scribe-cmd-debug ## build development binary with debug information

release: go-dependencies build-scribe-cmd ## build release version

# TODO: use tags
build-scribe-cmd-debug:
	cd scribe-service && CGO_ENABLED=0 go build -ldflags ${VERSION_LDFLAGS} -gcflags='all=-N -l' -o ./build/${GO_BINARY} ./cmd/main/

build-scribe-cmd:
	cd scribe-service && CGO_ENABLED=0 go build -ldflags ${VERSION_LDFLAGS} -o ./build/${GO_BINARY} ./cmd/main/

go-dependencies: ## download all golang dependencies
	cd scribe-service && go mod tidy && go mod download

.PHONY: swagger-generate
swagger-generate: ## generate Swagger client api library - client/api
	${SWAGGER} generate spec -m  \
		--exclude=github.com/sigstore/rekor/* \
		-o scribe-api.yaml cmd/main/server.go

.PHONY: swagger-generate-client
swagger-generate-client: swagger-client-clean ## generate Swagger client go library
	mkdir -p scribe-service/$(SWAGGER_GENERATED_DIR)
	${SWAGGER} generate client -t $(SWAGGER_GENERATED_DIR) -f $(SWAGGER_CONFIG)

.PHONY: swagger-client-clean
swagger-client-clean: ## clean Swagger client api library - client/api
	rm -rf  scribe-service/$(SWAGGER_GENERATED_DIR)

.PHONY: swagger-generate-old
swagger-generate-old: ## run it from scribe-service directory (OLD)
	docker run --rm -it  --user $(id -u):$(id -g) -e GOPATH=$(go env GOPATH):/go -v $(HOME):$(HOME) -w $(pwd) -e GOCACHE=/tmp/go-cache quay.io/goswagger/swagger generate spec -m \
					--exclude='github.com/sigstore/rekor/pkg/generated/*' \
					--exclude='github.com/scribe-security/etl-flows/etl/pkg/client' \
					--exclude='github.com/scribe-security/etl-flows/etl/pkg/testcontainer' \
					-o scribe-api.yaml cmd/main/server.go

.PHONY: upstream-base
upstream-cocosign:
	cd scribe-service; GOPRIVATE=github.com/scribe-security/* go get github.com/scribe-security/cocosign@master

generate-sqlc:
	mkdir -p scribe-service/migrations && \
		cp etl/migrations/create_user_and_schema.sql scribe-service/migrations/1_create_user_and_schema.sql && \
		cp etl/migrations/versions/temp_app.sql scribe-service/migrations/2_app_schema.sql && \
		(cd etl && alembic -x sqlc-migrations=true upgrade --sql head) \
		> scribe-service/migrations/3_osint_schema.sql && \
		sqlc -f scribe-service/sqlc.yaml generate && \
		rm -rf scribe-service/migrations

git-status:
	@status=$$(git status --porcelain); \
	if [ ! -z "$${status}" ]; \
	then \
		echo "Error - working directory is dirty. Commit those changes!"; \
		git --no-pager diff; \
		exit 1; \
	fi

git-status-pushed:
	@status=$$(git diff $(GIT_BRANCH)..origin/$(GIT_BRANCH)); \
	if [ ! -z "$${status}" ]; \
	then \
		echo "Error - local branch is not up-to-date. Pull and\or push"; \
		exit 1; \
	fi

# starts a deployment workflow for the current branch
# requires github-cli installed and authenticated
DEPLOYMENT_WORKFLOW_ID = deployment.yml
ENV = dev
run-workflow: git-status git-status-pushed
	# start workflow
	gh workflow --repo $(GITHUB_REPO_NAME) run --ref $(GIT_BRANCH) -f environment=$(ENV) $(DEPLOYMENT_WORKFLOW_ID)
	# wait for workflow to start
	sleep 1
	# open workflow page in browser
	@wf_id=$$(gh run list --repo $(GITHUB_REPO_NAME) --workflow=$(DEPLOYMENT_WORKFLOW_ID) --json databaseId |jq '.[0].databaseId'); \
	gh run view --web --repo $(GITHUB_REPO_NAME) $${wf_id} > /dev/null
