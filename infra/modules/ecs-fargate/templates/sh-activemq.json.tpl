  [
    {
            "dnsSearchDomains": null,
            "environmentFiles": null,
            "logConfiguration": {
                "logDriver": "awsfirelens",
                "secretOptions": null,
                "options": {
                    "LabelKeys": "container_id,container_name,ecs_task_definition,source,ecs_cluster",
                    "Labels": "{job=\"scribe-${environment}-sh-activemq\"}",
                    "LineFormat": "key_value",
                    "Name": "grafana-loki",
                    "RemoveKeys": "ecs_task_arn",
                    "Url": "http://scribe-${environment}-loki.scribe-${environment}-app-sd:3100/loki/api/v1/push"
                }
            },
            "entryPoint": null,
            "portMappings": [
                {
                    "containerPort": 8161,
                    "hostPort": 8161,
                    "protocol": "tcp"
                },
                {
                    "containerPort": 61616,
                    "hostPort": 61616,
                    "protocol": "tcp"
                }
            ],
            "command": [],
            "linuxParameters": null,
            "cpu": 0,
            "environment": [],
            "resourceRequirements": null,
            "ulimits": [],
            "dnsServers": null,
            "mountPoints": [],
            "workingDirectory": null,
            "secrets": [
                {
                    "name": "ARTEMIS_PASSWORD",
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/sh-backend/ACTIVE_MQ_PASSWORD"
                },
                {
                    "name": "ARTEMIS_USERNAME",
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/sh-backend/ACTIVE_MQ_USER"
                }
            ],
            "dockerSecurityOptions": null,
            "memory": null,
            "memoryReservation": null,
            "volumesFrom": [],
            "stopTimeout": null,
            "image": "${backend_account_id}.dkr.ecr.${backend_aws_region}.amazonaws.com/activemq-artemis:2.27.1",
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
            "name": "sh-${environment}-activemq"
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
            "name": "scribe-${environment}-sh-activemq-log-router"
        }
]

