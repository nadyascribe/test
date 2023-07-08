output "scheduler_task_definition_arn" {
  value = aws_ecs_task_definition.airflow-scheduler.arn
}

output "webserver_task_definition_arn" {
  value = aws_ecs_task_definition.airflow-webserver.arn
}

output "go_app_task_definition_arn" {
  value = aws_ecs_task_definition.airflow-go-app.arn
}

output "internal_api_task_definition_arn" {
  value = aws_ecs_task_definition.internal-api.arn
}

output "triggerer_task_definition_arn" {
  value = aws_ecs_task_definition.airflow-triggerer.arn
}

output "sh_backend_task_definition_arn" {
  value = aws_ecs_task_definition.sh-backend.arn
}

output "sh_activemq_task_definition_arn" {
  value = aws_ecs_task_definition.sh-activemq.arn
}

output "airflow-ecs-security-group" {
  value = aws_security_group.airflow-ecs.id
}