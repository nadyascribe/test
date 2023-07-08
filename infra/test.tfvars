# A name to describe the environment we're creating.
environment = "test"

# The AWS-CLI profile for the account to create resources in.
aws_profile = "scribe"

# The AWS region to create resources in.
aws_region = "us-west-2"

# The AWS account ID to create resources in.
account_id = "335681522553"

# The AWS availability zones to create subnets in.
# For high-availability, we need at least two.
availability_zones = ["us-west-2a", "us-west-2b"]

# The IP range to attribute to the virtual network.
# The allowed block size is between a /16 (65,536 addresses) and /28 (16 addresses).
vpc_cidr = "10.0.0.0/16"

# The VPC id
vpc_id = "vpc-060aee0f3b3aa5330"

# The IP ranges to use for the public subnets in your VPC.
# Must be within the IP range of your VPC.
public_subnet_cidrs = ["10.0.16.0/20", "10.0.48.0/20"]

# The IP ranges to use for the private subnets in your VPC.
# Must be within the IP range of your VPC.
private_subnet_cidrs = ["10.0.0.0/20", "10.0.32.0/20"]

public_subnet_ids = ["subnet-06bde5ea53242841c", "subnet-0cb95d81f0949cb8b"]

#Private Subnet IDs
private_subnet_ids   = ["subnet-0de17e240957900fd", "subnet-073d3e1e7e4cd280b"]
private_subnet_id_2a = "subnet-0de17e240957900fd"
private_subnet_id_2b = "subnet-073d3e1e7e4cd280b"

ecs_sh_container_port      = 80
ecs_airflow_container_port = 4000

airflow_health_check_path = "/health"
sh_health_check_path      = "/actuator/health"

# Network Mode For ECS
network_mode = "awsvpc"

# Properties of the database to be created in RDS and used by application
db_user          = "airflow"
db_name          = "airflow"
db_port          = 5432
db_instance_type = "db.t3.small"
sh_db_name       = "airflow"

# Airflow Core
airflow_core_executor                            = "LocalExecutor"
airflow_core_dags_paused_at_creation             = "True"
airflow_core_load_examples                       = "False"
airflow_uid                                      = 0
airflow_core_dagbag_import_error_traceback_depth = 10
airflow_database_load_default_connections        = "False"

# Airflow Init
airflow_db_upgrade              = "True"
airflow_www_user_create         = "True"
airflow_api_auth_backends       = "airflow.api.auth.backend.basic_auth"
sqlalchemy_silence_uber_warning = 1

request_logging_include_payload      = "true"
request_logging_include_query_string = "true"
mail_recipients_allowlist_enabled    = "true"
inform_about_expired_plans_enabled   = "true"
server_port                          = 80

active_mq_enabled = "true"
active_mq_port    = 61616

backend_aws_region = "eu-central-1"
backend_account_id = "775094898850"

domain_name = "scribehub"

aliases = ["scribehub.test.scribesecurity.com"]
