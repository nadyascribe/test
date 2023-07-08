variable "environment" {
  description = "The name of the environment"
}

variable "public_subnet_ids" {
  type        = list
  description = "List of public subnet ids to place the loadbalancer in"
}

variable "vpc_id" {
  description = "The VPC id"
}

variable "deregistration_delay" {
  default     = "300"
  description = "The default deregistration delay"
}

variable "airflow_health_check_path" {
  description = "The default airflow health check path"
}

variable "sh_health_check_path" {
  description = "The default sh health check path"
}

variable "vpc_cidr" {
  description = "Specify cidr block that is allowed to access the LoadBalancer"
}

variable "zone_id" {
  type = string
  description = "Route53 zone id"
}

variable "alb_certificate_arn" {
  description = "ACM Certificate"
}
