resource "aws_ecr_repository" "airflow-repo" {
  name                 = "scribe-sh-${var.environment}-app-airflow"
  image_tag_mutability = "MUTABLE"

  # image_scanning_configuration {
  #   scan_on_push = true
  # }
}