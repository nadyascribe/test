variable "airflow_ecs_cluster" {
  type = string
}

variable "network_mode" {
  description = "Network mode for activemq task definition"
}

variable "private_subnet_ids" {
  type        = list
  description = "The list of private subnets ids to use"
}

variable "private_subnet_id_2a" {
  description = "The list of private subnet id to use in efs"
}

variable "private_subnet_id_2b" {
  description = "The list of private subnet id to use in efs"
}

variable "vpc_cidr" {
  description = "VPC cidr block. Example: 10.0.0.0/16"
}

variable "scheduler_registry_arn" {
  description = "service discovery arn"
}

variable "webserver_registry_arn" {
  description = "service discovery arn"
}

variable "go_app_registry_arn" {
  description = "service discovery arn"
}

variable "triggerer_registry_arn" {
  description = "service discovery arn"
}

variable "internal_api_registry_arn" {
  description = "service discovery arn"
}

variable "sh_backend_registry_arn" {
  description = "service discovery arn"
}

variable "sh_activemq_registry_arn" {
  description = "service discovery arn"
}

variable "vpc_id" {
  description = "The VPC id"
}

variable "aws_region" {
  description = "Region"
}

variable "backend_aws_region" {
  description = "SH backend Region"
}

variable "environment" {
  description = "A name to describe the environment we're creating."
}

variable "account_id" {
  description = "Account ID to deploy"
}

variable "backend_account_id" {
  description = "SH Backend account ID to deploy"
}

variable "airflow_alb_target_group_arn" {
  type = string
}

variable "ecs_airflow_container_port" {
  type = number
}

variable "sh_alb_target_group_arn" {
  type = string
}

variable "ecs_sh_container_port" {
  type = number
}

variable "postgres_host_arn" {
  type = string
}