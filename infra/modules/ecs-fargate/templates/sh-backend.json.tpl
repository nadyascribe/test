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
                    "Labels": "{job=\"scribe-${environment}-sh-backend\"}",
                    "LabelKeys": "container_id,container_name,ecs_task_definition,source,ecs_cluster",
                    "Url": "http://scribe-${environment}-loki.scribe-${environment}-app-sd:3100/loki/api/v1/push",
                    "Name": "grafana-loki"
                }
            },
            "entryPoint": null,
            "portMappings": [
                {
                    "containerPort": 80,
                    "hostPort": 80,
                    "protocol": "tcp"
                }
            ],
            "command": [],
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
            "ulimits": [],
            "dnsServers": null,
            "mountPoints": [],
            "workingDirectory": null,
            "secrets": [
                {
                    "name": "ACTIVE_MQ_ENABLED",
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/sh-backend/ACTIVE_MQ_ENABLED"
                },
                {
                    "name": "ACTIVE_MQ_HOST",
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/sh-backend/ACTIVE_MQ_HOST"
                },
                {
                    "name": "ACTIVE_MQ_PASSWORD",
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/sh-backend/ACTIVE_MQ_PASSWORD"
                },
                {
                    "name": "ACTIVE_MQ_PORT",
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/sh-backend/ACTIVE_MQ_PORT"
                },
                {
                    "name": "ACTIVE_MQ_USER",
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/sh-backend/ACTIVE_MQ_USER"
                },
                {
                    "name": "AUTH0_AUDIENCE",
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/sh-backend/AUTH0_AUDIENCE"
                },
                {
                    "name": "AUTH0_CLIENT_ID",
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/sh-backend/AUTH0_CLIENT_ID"
                },
                {
                    "name": "AUTH0_CLIENT_PREFIX",
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/sh-backend/AUTH0_CLIENT_PREFIX"
                },
                {
                    "name": "AUTH0_CLIENT_SECRET",
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/sh-backend/AUTH0_CLIENT_SECRET"
                },
                {
                    "name": "AUTH0_DOMAIN",
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/sh-backend/AUTH0_DOMAIN"
                },
                {
                    "name": "AUTH0_REDIRECT_TOKEN_SECRET",
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/sh-backend/AUTH0_REDIRECT_TOKEN_SECRET"
                },
                {
                    "name": "AUTH0_SCRIBE_SERVICE_AUDIENCE",
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/sh-backend/AUTH0_SCRIBE_SERVICE_AUDIENCE"
                },
                {
                    "name": "BLUESNAP_WEBHOOK_ALLOWED_IP_ADDRESSES",
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/sh-backend/BLUESNAP_WEBHOOK_ALLOWED_IP_ADDRESSES"
                },
                {
                    "name": "DB_HOST",
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/airflow/POSTGRES_HOST"
                },
                {
                    "name": "DB_NAME",
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/sh-backend/POSTGRES_DB"
                },
                {
                    "name": "DB_PASSWORD",
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/airflow/POSTGRES_PASSWORD"
                },
                {
                    "name": "DB_PORT",
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/airflow/POSTGRES_PORT"
                },
                {
                    "name": "DB_USER",
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/airflow/POSTGRES_USER"
                },
                {
                    "name": "GITHUB_APP_URL",
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/sh-backend/GITHUB_APP_URL"
                },
                {
                    "name": "GITHUB_INTEGRATION_TOKEN_SECRET",
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/sh-backend/GITHUB_INTEGRATION_TOKEN_SECRET"
                },
                {
                    "name": "GOOGLE_WORKLOAD_IDENTITY_PROVIDER",
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/sh-backend/GOOGLE_WORKLOAD_IDENTITY_PROVIDER"
                },
                {
                    "name": "INFORM_ABOUT_EXPIRED_PLANS_EMAILS",
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/sh-backend/INFORM_ABOUT_EXPIRED_PLANS_EMAILS"
                },
                {
                    "name": "INFORM_ABOUT_EXPIRED_PLANS_ENABLED",
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/sh-backend/INFORM_ABOUT_EXPIRED_PLANS_ENABLED"
                },
                {
                    "name": "INTERNAL_API_PASSWORD",
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/sh-backend/INTERNAL_API_PASSWORD"
                },
                {
                    "name": "LAUNCHDARKLY_SDK_KEY",
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/sh-backend/LAUNCHDARKLY_SDK_KEY"
                },
                {
                    "name": "MAIL_ADDRESS_FROM",
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/sh-backend/MAIL_ADDRESS_FROM"
                },
                {
                    "name": "MAIL_RECIPIENTS_ALLOWLIST_ENABLED",
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/sh-backend/MAIL_RECIPIENTS_ALLOWLIST_ENABLED"
                },
                {
                    "name": "REQUEST_LOGGING_INCLUDE_PAYLOAD",
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/sh-backend/REQUEST_LOGGING_INCLUDE_PAYLOAD"
                },
                {
                    "name": "REQUEST_LOGGING_INCLUDE_QUERY_STRING",
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/sh-backend/REQUEST_LOGGING_INCLUDE_QUERY_STRING"
                },
                {
                    "name": "SCRIBE_API_BASE_URI",
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/sh-backend/SCRIBE_API_BASE_URI"
                },
                {
                    "name": "SCRIBE_HUB_APP_URL",
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/sh-backend/SCRIBE_HUB_APP_URL"
                },
                {
                    "name": "SENDGRID_API_KEY",
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/sh-backend/SENDGRID_API_KEY"
                },
                {
                    "name": "SERVER_PORT",
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/sh-backend/SERVER_PORT"
                },
                {
                    "name": "STATISTICS_SPREADSHEET_ID",
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/sh-backend/STATISTICS_SPREADSHEET_ID"
                }
            ],
            "dockerSecurityOptions": null,
            "memory": null,
            "memoryReservation": null,
            "volumesFrom": [],
            "stopTimeout": null,
            "image": "${backend_account_id}.dkr.ecr.${backend_aws_region}.amazonaws.com/scribe-hub-api:v0.36.0",
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
            "name": "sh-${environment}-backend"
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
            "name": "scribe-${environment}-sh-backend-log-router"
        }
]
