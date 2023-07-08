[
    {
        "name": "airflow-${environment}-alembic",
        "image": "${account_id}.dkr.ecr.${aws_region}.amazonaws.com/scribe-sh-${environment}-app-airflow:latest",
        "cpu": 0,
        "portMappings": [],
        "essential": true,
        "entryPoint": [
            "alembic",
            "upgrade",
            "head"
        ],
        "environment": [],
        "mountPoints": [],
        "volumesFrom": [],
        "secrets": [
            {
                "name": "_AIRFLOW_DB_UPGRADE",
                "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/airflow/_AIRFLOW_DB_UPGRADE"
            },
            {
                "name": "_AIRFLOW_WWW_USER_CREATE",
                "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/airflow/_AIRFLOW_WWW_USER_CREATE"
            },
            {
                "name": "_AIRFLOW_WWW_USER_PASSWORD",
                "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/airflow/_AIRFLOW_WWW_USER_PASSWORD"
            },
            {
                "name": "_AIRFLOW_WWW_USER_USERNAME",
                "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/airflow/_AIRFLOW_WWW_USER_USERNAME"
            },
            {
                "name": "AIRFLOW__CORE__DAGBAG_IMPORT_ERROR_TRACEBACK_DEPTH",
                "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/airflow/AIRFLOW__CORE__DAGBAG_IMPORT_ERROR_TRACEBACK_DEPTH"
            },
            {
                "name": "AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION",
                "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/airflow/AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION"
            },
            {
                "name": "AIRFLOW__CORE__EXECUTOR",
                "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/airflow/AIRFLOW__CORE__EXECUTOR"
            },
            {
                "name": "AIRFLOW__CORE__FERNET_KEY",
                "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/airflow/AIRFLOW__CORE__FERNET_KEY"
            },
            {
                "name": "AIRFLOW__CORE__LOAD_EXAMPLES",
                "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/airflow/AIRFLOW__CORE__LOAD_EXAMPLES"
            },
            {
                "name": "AIRFLOW__DATABASE__LOAD_DEFAULT_CONNECTIONS",
                "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/airflow/AIRFLOW__DATABASE__LOAD_DEFAULT_CONNECTIONS"
            },
            {
                "name": "AIRFLOW__DATABASE__SQL_ALCHEMY_CONN",
                "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/airflow/AIRFLOW__DATABASE__SQL_ALCHEMY_CONN"
            },
            {
                "name": "AIRFLOW_CONN_GCS_DEFAULT",
                "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/airflow/GCS_DEFAULT_CONN"
            },
            {
                "name": "AIRFLOW_CONN_POSTGRES_DEFAULT",
                "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/airflow/POSTGRES_DEFAULT_CONN"
            },
            {
                "name": "AIRFLOW_CONN_S3_CONN",
                "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/airflow/S3_CONN"
            },
            {
                "name": "AIRFLOW_UID",
                "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/airflow/AIRFLOW_UID"
            },
            {
                "name": "POSTGRES_DB",
                "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/airflow/POSTGRES_DB"
            },
            {
                "name": "POSTGRES_HOST",
                "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/airflow/POSTGRES_HOST"
            },
            {
                "name": "POSTGRES_PASSWORD",
                "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/airflow/POSTGRES_PASSWORD"
            },
            {
                "name": "POSTGRES_USER",
                "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/airflow/POSTGRES_USER"
            },
            {
                "name": "SQLALCHEMY_SILENCE_UBER_WARNING",
                "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/airflow/SQLALCHEMY_SILENCE_UBER_WARNING"
            }
        ],
        "user": "50000:0",
        "logConfiguration": {
            "logDriver": "awsfirelens",
            "options": {
                "LabelKeys": "container_id,container_name,ecs_task_definition,source,ecs_cluster",
                "Labels": "{job=\"scribe-${environment}-airflow-alembic\"}",
                "LineFormat": "key_value",
                "Name": "grafana-loki",
                "RemoveKeys": "ecs_task_arn",
                "Url": "http://scribe-${environment}-loki.scribe-${environment}-app-sd:3100/loki/api/v1/push"
            }
        }
    },
    {
        "name": "scribe-${environment}-alembic-log-router",
        "image": "${account_id}.dkr.ecr.${aws_region}.amazonaws.com/scribe-airflow-fluentbit:latest",
        "cpu": 0,
        "portMappings": [],
        "essential": true,
        "environment": [],
        "mountPoints": [],
        "volumesFrom": [],
        "user": "0",
        "logConfiguration": {
            "logDriver": "awslogs",
            "options": {
                "awslogs-group": "${awslogs-group}",
                "awslogs-region": "${aws_region}",
                "awslogs-stream-prefix": "ecs"
            }
        },
        "firelensConfiguration": {
            "type": "fluentbit",
            "options": {
                "enable-ecs-log-metadata": "true"
            }
        }
    }
]