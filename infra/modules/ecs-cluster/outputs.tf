output "ecs_cluster" {
  value = aws_ecs_cluster.airflow-cluster.id
}

# output "vpc_id" {
#   value = module.network.vpc_id
# }

# output "private_subnet_ids" {
#   value = module.network.private_subnet_ids
# }