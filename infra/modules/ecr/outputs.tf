output "airflow_image_repo_url" {
  value = aws_ecr_repository.airflow-repo.repository_url
}

output "airflow_image_repo_arn" {
  value = aws_ecr_repository.airflow-repo.arn
}
