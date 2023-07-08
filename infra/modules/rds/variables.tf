variable "environment" {
  description = "A name to describe the environment we're creating."
}

variable "db_name" {
  description = "Database Name"
}

variable "db_password" {
  description = "Database Password"
}

variable "db_user" {
  description = "Database username"
}

variable "db_port" {
  description = "Database Port"
}

variable "db_instance_type" {
  description = "Database Instance Type"
}

variable "vpc_id" {
  description = "VPC id"
}

variable "vpc_cidr" {
  description = "The IP range to attribute to the virtual network."
}

variable "private_subnet_ids" {
  description = "VPC id"
}

variable "airflow-ecs-security-group" {
  description = "Airflow ECS VPC id"
}