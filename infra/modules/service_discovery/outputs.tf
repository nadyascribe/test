output "scheduler_service_discovery" {
  value = aws_service_discovery_service.airflow_scheduler.arn
}

output "webserver_service_discovery" {
  value = aws_service_discovery_service.airflow_webserver.arn
}

output "go_app_service_discovery" {
  value = aws_service_discovery_service.airflow_go_app.arn
}

output "triggerer_service_discovery" {
  value = aws_service_discovery_service.airflow_triggerer.arn
}

output "sh_backend_service_discovery" {
  value = aws_service_discovery_service.sh_backend.arn
}

output "sh_activemq_service_discovery" {
  value = aws_service_discovery_service.sh_activemq.arn
}

output "internal_api_service_discovery" {
  value = aws_service_discovery_service.internal_api.arn
}