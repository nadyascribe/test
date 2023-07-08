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
                    "Labels": "{job=\"scribe-${environment}-airflow-go-app\"}",
                    "LabelKeys": "container_id,container_name,ecs_task_definition,source,ecs_cluster",
                    "Url": "http://scribe-${environment}-loki.scribe-${environment}-app-sd:3100/loki/api/v1/push",
                    "Name": "grafana-loki"
                }
            },
            "entryPoint": null,
            "portMappings": [
                {
                    "hostPort": 4000,
                    "protocol": "tcp",
                    "containerPort": 4000
                }
            ],
            "command": [
                "/opt/scribe-service",
                "server"
            ],
            "linuxParameters": null,
            "cpu": 0,
            "environment": [
                {
                    "name": "NAMESPACE",
                    "value": "scribe-${environment}-app-sd"
                }
            ],
            "resourceRequirements": null,
            "ulimits": null,
            "dnsServers": null,
            "mountPoints": [],
            "workingDirectory": null,
            "secrets": [
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
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/airflow/POSTGRES_PORT",
                    "name": "POSTGRES_PORT"
                },
                {
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/airflow/POSTGRES_USER",
                    "name": "POSTGRES_USER"
                },
                {
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/airflow/SCRIBE_ENVIRONMENT",
                    "name": "SCRIBE_ENVIRONMENT"
                },
                {
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/airflow/_AIRFLOW_WWW_USER_USERNAME",
                    "name": "AIRFLOW_LOGIN"
                },
                {
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/airflow/_AIRFLOW_WWW_USER_PASSWORD",
                    "name": "AIRFLOW_PASSWORD"
                },
                {
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/airflow/GITHUB_V3_API_URL",
                    "name": "GITHUB_V3_API_URL"
                },
                {
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/airflow/GITHUB_APP_WEBHOOK_SECRET",
                    "name": "GITHUB_APP_WEBHOOK_SECRET"
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
            "user": null,
            "readonlyRootFilesystem": null,
            "dockerLabels": null,
            "systemControls": null,
            "privileged": null,
            "name": "airflow-${environment}-go-app"
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
            "memoryReservation": 50,
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
            "name": "airflow-${environment}-go-app-log-router"
        }
]
