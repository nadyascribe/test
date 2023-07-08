# module "network" {
#   source               = "../network"
  
#   environment          = var.environment
#   vpc_cidr             = var.vpc_cidr
#   private_subnet_cidrs = var.private_subnet_cidrs
#   availability_zones   = var.availability_zones
# }

resource "aws_ecs_cluster" "airflow-cluster" {
  name = "scribe-sh-app-${var.environment}"
  setting {
    name = "containerInsights"
    value = "enabled"
  }
}

