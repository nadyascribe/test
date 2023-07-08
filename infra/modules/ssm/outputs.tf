output "postgres_host_arn" {
  value = aws_ssm_parameter.postgres_host.arn
}