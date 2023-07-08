[
    {
            "dnsSearchDomains": null,
            "environmentFiles": null,
            "logConfiguration": {
                "logDriver": "awsfirelens",
                "secretOptions": null,
                "options": {
                    "RemoveKeys": "ecs_task_arn",
                    "LineFormat": "key_value",
                    "Labels": "{job=\"scribe-${environment}-airflow-webserver\"}",
                    "LabelKeys": "container_id,container_name,ecs_task_definition,source,ecs_cluster",
                    "Url": "http://scribe-${environment}-loki.scribe-${environment}-app-sd:3100/loki/api/v1/push",
                    "Name": "grafana-loki"
                }
            },
            "portMappings": [
                {
                    "hostPort": 8080,
                    "protocol": "tcp",
                    "containerPort": 8080
                }
            ],
            "entryPoint": [
                "/entrypoint"
            ],
            "command": [
                "webserver"
            ],
            "linuxParameters": null,
            "cpu": 0,
            "environment": [
                {
                    "name": "ENVIRONMENT",
                    "value": "${environment}"
                },
                {
                    "name": "NAMESPACE",
                    "value": "scribe-${environment}-app-sd"
                }
            ],
            "resourceRequirements": null,
            "ulimits": [
                {
                    "name": "nofile",
                    "softLimit": 65536,
                    "hardLimit": 65536
                }
            ],
            "dnsServers": null,
            "mountPoints": [
                {
                    "readOnly": false,
                    "containerPath": "/opt/airflow/logs",
                    "sourceVolume": "airflow-logs"
                }
            ],
            "workingDirectory": null,
            "secrets": [
                {
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/airflow/_AIRFLOW_DB_UPGRADE",
                    "name": "_AIRFLOW_DB_UPGRADE"
                },
                {
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/airflow/_AIRFLOW_WWW_USER_CREATE",
                    "name": "_AIRFLOW_WWW_USER_CREATE"
                },
                {
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/airflow/_AIRFLOW_WWW_USER_PASSWORD",
                    "name": "_AIRFLOW_WWW_USER_PASSWORD"
                },
                {
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/airflow/_AIRFLOW_WWW_USER_USERNAME",
                    "name": "_AIRFLOW_WWW_USER_USERNAME"
                },
                {
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/airflow/AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION",
                    "name": "AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION"
                },
                {
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/airflow/AIRFLOW__CORE__EXECUTOR",
                    "name": "AIRFLOW__CORE__EXECUTOR"
                },
                {
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/airflow/AIRFLOW__CORE__FERNET_KEY",
                    "name": "AIRFLOW__CORE__FERNET_KEY"
                },
                {
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/airflow/AIRFLOW__CORE__LOAD_EXAMPLES",
                    "name": "AIRFLOW__CORE__LOAD_EXAMPLES"
                },
                {
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/airflow/AIRFLOW__DATABASE__LOAD_DEFAULT_CONNECTIONS",
                    "name": "AIRFLOW__DATABASE__LOAD_DEFAULT_CONNECTIONS"
                },
                {
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/airflow/AIRFLOW__DATABASE__SQL_ALCHEMY_CONN",
                    "name": "AIRFLOW__DATABASE__SQL_ALCHEMY_CONN"
                },
                {
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/airflow/AIRFLOW_UID",
                    "name": "AIRFLOW_UID"
                },
                {
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/airflow/POSTGRES_DB",
                    "name": "POSTGRES_DB"
                },
                {
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/airflow/POSTGRES_HOST",
                    "name": "POSTGRES_HOST"
                },
                {
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/airflow/POSTGRES_PASSWORD",
                    "name": "POSTGRES_PASSWORD"
                },
                {
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/airflow/POSTGRES_USER",
                    "name": "POSTGRES_USER"
                },
                {
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/airflow/AIRFLOW__CORE__DAGBAG_IMPORT_ERROR_TRACEBACK_DEPTH",
                    "name": "AIRFLOW__CORE__DAGBAG_IMPORT_ERROR_TRACEBACK_DEPTH"
                },
                {
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/airflow/POSTGRES_DEFAULT_CONN",
                    "name": "AIRFLOW_CONN_POSTGRES_DEFAULT"
                },
                {
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/airflow/S3_CONN",
                    "name": "AIRFLOW_CONN_S3_CONN"
                },
                {
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/airflow/GCS_DEFAULT_CONN",
                    "name": "AIRFLOW_CONN_GCS_DEFAULT"
                },
                {
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/airflow/GRYPE_PATH",
                    "name": "AIRFLOW_VAR_GRYPE_PATH"
                },
                {
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/airflow/SHARED_DIRECTORY",
                    "name": "AIRFLOW_VAR_SHARED_DIRECTORY"
                },
                {
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/airflow/GCS_PACKAGE_VERSION",
                    "name": "AIRFLOW_VAR_GCS_PACKAGE_VERSION_TO_PROJECT_SOURCE"
                },
                {
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/airflow/SQLALCHEMY_SILENCE_UBER_WARNING",
                    "name": "SQLALCHEMY_SILENCE_UBER_WARNING"
                },
                {
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/airflow/AIRFLOW__API__AUTH_BACKENDS",
                    "name": "AIRFLOW__API__AUTH_BACKENDS"
                },
                {
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/sh-backend/SCRIBE_API_BASE_URI",
                    "name": "SCRIBE_API_BASE_URI"
                },
                {
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/sh-backend/AUTH0_DOMAIN",
                    "name": "AUTH0_DOMAIN"
                },
                {
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/sh-backend/AUTH0_SCRIBE_SERVICE_AUDIENCE",
                    "name": "AUTH0_SCRIBE_SERVICE_AUDIENCE"
                }
            ],
            "dockerSecurityOptions": null,
            "memory": null,
            "memoryReservation": null,
            "volumesFrom": [],
            "stopTimeout": null,
            "image": "${account_id}.dkr.ecr.${aws_region}.amazonaws.com/scribe-sh-${environment}-app-airflow:latest",
            "startTimeout": null,
            "firelensConfiguration": null,
            "dependsOn": null,
            "disableNetworking": null,
            "interactive": null,
            "healthCheck": null,
            "essential": true,
            "links": null,
            "hostname": null,
            "extraHosts": null,
            "pseudoTerminal": null,
            "user": "0:0",
            "readonlyRootFilesystem": null,
            "dockerLabels": null,
            "systemControls": null,
            "privileged": null,
            "name": "airflow-${environment}-webserver"
        },
        {
            "dnsSearchDomains": null,
            "environmentFiles": null,
            "logConfiguration": {
                "logDriver": "awslogs",
                "secretOptions": null,
                "options": {
                    "awslogs-group": "${awslogs-group}",
                    "awslogs-region": "${aws_region}",
                    "awslogs-stream-prefix": "ecs"
                }
            },
            "entryPoint": null,
            "portMappings": [],
            "command": null,
            "linuxParameters": null,
            "cpu": 0,
            "environment": [],
            "resourceRequirements": null,
            "ulimits": null,
            "dnsServers": null,
            "mountPoints": [],
            "workingDirectory": null,
            "secrets": null,
            "dockerSecurityOptions": null,
            "memory": null,
            "memoryReservation": null,
            "volumesFrom": [],
            "stopTimeout": null,
            "image": "${account_id}.dkr.ecr.${aws_region}.amazonaws.com/scribe-airflow-fluentbit:latest",
            "startTimeout": null,
            "firelensConfiguration": {
                "type": "fluentbit",
                "options": {
                    "enable-ecs-log-metadata": "true"
                }
            },
            "dependsOn": null,
            "disableNetworking": null,
            "interactive": null,
            "healthCheck": null,
            "essential": true,
            "links": null,
            "hostname": null,
            "extraHosts": null,
            "pseudoTerminal": null,
            "user": "0",
            "readonlyRootFilesystem": null,
            "dockerLabels": null,
            "systemControls": null,
            "privileged": null,
            "name": "airflow-${environment}-webserver-log-router"
        }
]