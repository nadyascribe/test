FROM golang:1.20.2-alpine3.17 as go_builder

ARG PERSONAL_TOKEN
ARG GIT_USER
ARG GITHUB_POSTURE_BRANCH
ENV GOPRIVATE="github.com/scribe-security/*"

RUN apk update && apk upgrade && \
    apk --update add git make ca-certificates curl

RUN git config --global url."https://$GIT_USER:$PERSONAL_TOKEN@github.com".insteadOf "https://github.com"

RUN git clone -b "main" --single-branch "https://github.com/scribe-security/GitHub-Posture" /opt/GitHub-Posture
RUN git clone -b main --single-branch "https://github.com/scribe-security/chain-bench.git" /opt/chain-bench && \
    cd /opt/chain-bench && \
    make build

WORKDIR /app

COPY scribe-service ./scribe-service
COPY Makefile .

# Build
RUN GOOS=linux GOARCH=amd64 make release

FROM apache/airflow:slim-2.6.1-python3.10

RUN chown -R 50000:root /opt/airflow/dags

USER root
# install grype

RUN apt-get update && apt-get install -y skopeo
RUN curl -sSfL https://raw.githubusercontent.com/anchore/grype/main/install.sh | \
    sh -s -- -b /opt/grype v0.59.0 &&  \
    ls /opt/grype/grype # check if grype is installed

RUN curl -sSfL https://get.scribesecurity.com/install.sh | \
    sh -s -- -t valint:0.2.0 -b /opt/valint && ls /opt/valint/valint

USER airflow
COPY ./etl/requirements.txt /opt/airflow/requirements.txt
RUN pip3 install --user --upgrade pip
RUN pip3 install --no-cache-dir --user -r /opt/airflow/requirements.txt

COPY ./etl/alembic.ini /opt/airflow/alembic.ini
COPY ./etl/.grype.yaml /opt/grype/.grype.yaml

COPY --chown=0:0 --from=go_builder /app/scribe-service/build/scribe-service /opt/scribe-service
COPY --chown=0:0 --from=go_builder /opt/chain-bench/chain-bench /opt/chain-bench
COPY --chown=0:0 --from=go_builder /etc/ssl/certs/ca-certificates.crt /etc/ssl/certs/
COPY --chown=0:0 --from=go_builder /opt/GitHub-Posture /opt/GitHub-Posture

COPY ./scribe-service/configs ./configs

COPY ./etl/migrations /opt/airflow/migrations
COPY ./etl/dags /opt/airflow/dags
COPY ./etl/internal-api/app /internal-api/code/app

ENTRYPOINT []