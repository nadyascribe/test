[
       {
            "name": "postgres-${environment}-init",
            "image": "postgres:14",
            "cpu": 0,
            "portMappings": [],
            "essential": true,
            "command": [
                "bin/sh",
                "-c",
                "psql -h $POSTGRES_HOST -U $POSTGRES_USER -c \"CREATE USER osint WITH ENCRYPTED PASSWORD 'osint';\" -c \"CREATE SCHEMA IF NOT EXISTS osint;\" -c \"GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA osint TO osint;\" -c \"GRANT USAGE,CREATE ON SCHEMA osint,public TO osint;\""
            ],
            "secrets": [
                {
                    "valueFrom": "${postgres_host_arn}",
                    "name": "POSTGRES_HOST"
                },
                {                
                    "name": "BACKEND_DB",
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/sh-backend/POSTGRES_DB"
                },
                {
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/airflow/POSTGRES_USER",
                    "name": "POSTGRES_USER"
                },
                {
                    "name": "PGPASSWORD",
                    "valueFrom": "arn:aws:ssm:${aws_region}:${account_id}:parameter/${environment}/airflow/POSTGRES_PASSWORD"
                }
            ],
            "mountPoints": [],
            "volumesFrom": [],
            "logConfiguration": {
                "logDriver": "awslogs",
                "options": {
                    "awslogs-group": "${awslogs-group}",
                    "awslogs-region": "${aws_region}",
                    "awslogs-stream-prefix": "ecs"
                }
            }
        }
]