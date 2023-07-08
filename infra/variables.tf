variable "environment" {
  description = "A name to describe the environment we're creating."
}

variable "aws_profile" {
  description = "The AWS-CLI profile for the account to create resources in."
}

variable "account_id" {
  description = "Account ID to deploy"
}

variable "vpc_id" {
  description = "The VPC id"
}

variable "aws_region" {
  description = "The AWS region to create resources in."
}

variable "vpc_cidr" {
  description = "The IP range to attribute to the virtual network."
}

variable "sh_db_name" {
  description = "SH backend Postgres DB Name"
}

variable "aliases" {
  description = "alternate domain name"
}

variable "public_subnet_cidrs" {
  description = "The IP ranges to use for the public subnets in your VPC."
  type        = list(any)
}

variable "backend_aws_region" {
  description = "SH backend Region"
}

variable "backend_account_id" {
  description = "SH Backend account ID to deploy"
}

variable "public_subnet_ids" {
  type        = list(any)
  description = "List of public subnet ids to place the loadbalancer in"
}

variable "private_subnet_cidrs" {
  description = "The IP ranges to use for the private subnets in your VPC."
  type        = list(any)
}

variable "availability_zones" {
  description = "The AWS availability zones to create subnets in."
  type        = list(any)
}

# variable "deregistration_delay" {
#   default     = "300"
#   description = "The default deregistration delay"
# }

variable "private_subnet_ids" {
  type        = list(any)
  description = "The list of private subnets ids to use"
}

variable "private_subnet_id_2a" {
  description = "The list of private subnet id to use in efs"
}

variable "private_subnet_id_2b" {
  description = "The list of private subnet id to use in efs"
}

variable "db_name" {
  description = "Database Name"
}

variable "db_user" {
  description = "Database Password"
}

variable "db_port" {
  description = "Database Port"
}

variable "db_instance_type" {
  description = "Database Instance Type"
}

variable "network_mode" {
  description = "Network mode for activemq task definition"
}

variable "airflow_uid" {
  description = "Airflow UID"
}

variable "airflow_core_dags_paused_at_creation" {
  description = "AIRFLOW CORE DAGS ARE PAUSED AT CREATION"
}

variable "airflow_core_executor" {
  description = "Airflow Core Executor"
}

variable "airflow_core_load_examples" {
  description = "AIRFLOW CORE LOAD EXAMPLES"
}

variable "airflow_database_load_default_connections" {
  description = "AIRFLOW DATABASE LOAD DEFAULT CONNECTIONS"
}

variable "sqlalchemy_silence_uber_warning" {
  description = "SQLALCHEMY SILENCE UBER WARNING"
}

variable "airflow_db_upgrade" {
  description = "AIRFLOW DB UPGRADE"
}

variable "airflow_www_user_create" {
  description = "AIRFLOW WWW USER CREATE"
}

variable "airflow_api_auth_backends" {
  description = "AIRFLOW API AUTH BACKENDS"
}

variable "airflow_core_dagbag_import_error_traceback_depth" {
  description = "Airflow core dagbag import error traceback depth"
}

variable "mail_recipients_allowlist_enabled" {
  default     = true
  description = "Allow sending emails to the domain other than 7bulls.com and scribe.com"
}

variable "request_logging_include_query_string" {
  default     = true
  description = "Logging of the querystrings"
}

variable "request_logging_include_payload" {
  description = "Logging of the payloads"
}

variable "inform_about_expired_plans_enabled" {
  description = "Enable sending notifications on team plan subscription expiry."
}

variable "active_mq_enabled" {
  default     = true
  description = "Use ActiveMQ for websocket connections"
}

variable "server_port" {
  type = string
}

variable "active_mq_port" {
  type = string
}

variable "ecs_sh_container_port" {
  type = number
}

variable "ecs_airflow_container_port" {
  type = number
}

variable "airflow_health_check_path" {
  description = "The default airflow health check path"
}

variable "sh_health_check_path" {
  description = "The default sh health check path"
}

variable "domain_name" {
  description = "name of domain"
}