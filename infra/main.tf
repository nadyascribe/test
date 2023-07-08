data "aws_secretsmanager_secret" "sh_secrets" {
  name = "sh-${var.environment}-secrets"
}

data "aws_secretsmanager_secret_version" "sh_secrets_version" {
  secret_id = data.aws_secretsmanager_secret.sh_secrets.id
}

locals {
  sh_secrets = jsondecode(
    data.aws_secretsmanager_secret_version.sh_secrets_version.secret_string
  )
}

provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile
}

module "ecr" {
  source      = "./modules/ecr"
  environment = var.environment
}

module "rds" {
  source = "./modules/rds"

  environment                = var.environment
  db_name                    = var.db_name
  db_password                = local.sh_secrets.DB_PASSWORD
  db_user                    = var.db_user
  db_port                    = var.db_port
  db_instance_type           = var.db_instance_type
  vpc_id                     = var.vpc_id
  vpc_cidr                   = var.vpc_cidr
  private_subnet_ids         = var.private_subnet_ids
  airflow-ecs-security-group = module.ecs-fargate.airflow-ecs-security-group
}

module "ecs-cluster" {
  source = "./modules/ecs-cluster"

  environment = var.environment
}

module "service_discovery" {
  source          = "./modules/service_discovery"
  environment     = var.environment
  sd_namespace_id = local.sh_secrets.SD_NAMESPACE_ID
}

module "ssm" {
  source      = "./modules/ssm"
  environment = var.environment

  //RDS Database
  db_host     = module.rds.db_host
  db_name     = var.db_name
  db_password = local.sh_secrets.DB_PASSWORD
  db_port     = var.db_port
  db_user     = var.db_user
  sh_db_name  = var.sh_db_name

  // github app
  github_v3_api_url         = "https://api.github.com/"
  github_app_integration_id = local.sh_secrets.GITHUB_APP_INTEGRATION_ID
  // must be quoted, check that '/' symbol is quoted too
  github_app_private_key    = local.sh_secrets.GITHUB_APP_PRIVATE_KEY
  github_app_webhook_secret = local.sh_secrets.GITHUB_APP_WEBHOOK_SECRET

  scribe_almighty_fernet_key     = local.sh_secrets.SCRIBE_ALMIGHTY_FERNET_KEY
  s3_conn                        = local.sh_secrets.S3_CONN
  gcs_default_conn               = local.sh_secrets.GCS_DEFAULT_CONN
  auth0_client_id                = local.sh_secrets.AUTH0_CLIENT_ID
  auth0_client_secret            = local.sh_secrets.AUTH0_CLIENT_SECRET
  sendgrid_api_key               = local.sh_secrets.SENDGRID_API_KEY
  auth0_redirect_token_secret    = local.sh_secrets.AUTH0_REDIRECT_TOKEN_SECRET
  slack_webhook_airflow_failures = local.sh_secrets.SLACK_WEBHOOK_AIRFLOW_FAILURES

  scribe_hub_app_url = local.sh_secrets.SCRIBE_HUB_APP_URL

  internal_api_password           = local.sh_secrets.INTERNAL_API_PASSWORD
  launchdarkly_sdk_key            = local.sh_secrets.LAUNCHDARKLY_SDK_KEY
  github_integration_token_secret = local.sh_secrets.GITHUB_INTEGRATION_TOKEN_SECRET
  activemq_password               = local.sh_secrets.ACTIVE_MQ_PASSWORD

  airflow_uid                                      = var.airflow_uid
  airflow_core_dags_paused_at_creation             = var.airflow_core_dags_paused_at_creation
  airflow_core_executor                            = var.airflow_core_executor
  airflow_core_fernet_key                          = local.sh_secrets.AIRFLOW__CORE__FERNET_KEY
  airflow_core_load_examples                       = var.airflow_core_load_examples
  airflow_database_load_default_connections        = var.airflow_database_load_default_connections
  sqlalchemy_silence_uber_warning                  = var.sqlalchemy_silence_uber_warning
  airflow_db_upgrade                               = var.airflow_db_upgrade
  airflow_www_user_create                          = var.airflow_www_user_create
  airflow_api_auth_backends                        = var.airflow_api_auth_backends
  airflow_www_user_password                        = local.sh_secrets.AIRFLOW_WWW_USER_PASSWORD
  airflow_www_username                             = local.sh_secrets.AIRFLOW_WWW_USERNAME
  airflow_core_dagbag_import_error_traceback_depth = var.airflow_core_dagbag_import_error_traceback_depth

  shared_directory                      = local.sh_secrets.SHARED_DIRECTORY
  gcs_package_version_to_project_source = local.sh_secrets.GCS_PACKAGE_VERSION

  // set binaries paths explicitly here because they are managed within the `Dockerfile` of the current repo
  grype_path                 = "/opt/grype/grype"
  scribe_service_bin_path    = "/opt/scribe-service"
  github_posture_policy_path = "/opt/GitHub-Posture"
  chainbench_bin_path        = "/opt/chain-bench"

  //Auth0
  auth0_audience                = local.sh_secrets.AUTH0_AUDIENCE
  auth0_client_prefix           = local.sh_secrets.AUTH0_CLIENT_PREFIX
  auth0_domain                  = local.sh_secrets.AUTH0_DOMAIN
  auth0_scribe_service_audience = local.sh_secrets.AUTH0_SCRIBE_SERVICE_AUDIENCE

  request_logging_include_payload       = var.request_logging_include_payload
  request_logging_include_query_string  = var.request_logging_include_query_string
  mail_recipients_allowlist_enabled     = var.mail_recipients_allowlist_enabled
  scribe_api_base_uri                   = local.sh_secrets.SCRIBE_API_BASE_URI
  statistics_spreadsheet_id             = local.sh_secrets.STATISTICS_SPREADSHEET_ID
  google_workload_identity_provider     = local.sh_secrets.GOOGLE_WORKLOAD_IDENTITY_PROVIDER
  github_app_url                        = local.sh_secrets.GITHUB_APP_URL
  bluesnap_webhook_allowed_ip_addresses = local.sh_secrets.BLUESNAP_WEBHOOK_ALLOWED_IP_ADDRESSES
  inform_about_expired_plans_enabled    = var.inform_about_expired_plans_enabled
  inform_about_expired_plans_emails     = local.sh_secrets.INFORM_ABOUT_EXPIRED_PLANS_EMAILS

  server_port       = var.server_port
  mail_address_from = local.sh_secrets.MAIL_ADDRESS_FROM

  //ActiveMQ
  active_mq_enabled = var.active_mq_enabled
  active_mq_user    = local.sh_secrets.ACTIVE_MQ_USER
  active_mq_host    = local.sh_secrets.ACTIVE_MQ_HOST
  active_mq_port    = var.active_mq_port
}

module "alb" {
  source = "./modules/alb"

  environment               = var.environment
  vpc_id                    = var.vpc_id
  public_subnet_ids         = var.public_subnet_ids
  airflow_health_check_path = var.airflow_health_check_path
  sh_health_check_path      = var.sh_health_check_path
  vpc_cidr                  = var.vpc_cidr
  zone_id                   = local.sh_secrets.ZONE_ID
  alb_certificate_arn       = local.sh_secrets.ALB_CERTIFICATE_ARN
}

module "ecs-fargate" {
  source = "./modules/ecs-fargate"

  account_id          = var.account_id
  airflow_ecs_cluster = module.ecs-cluster.ecs_cluster
  vpc_id              = var.vpc_id
  network_mode        = var.network_mode
  private_subnet_ids  = var.private_subnet_ids
  vpc_cidr            = var.vpc_cidr
  postgres_host_arn   = module.ssm.postgres_host_arn

  private_subnet_id_2a = var.private_subnet_id_2a
  private_subnet_id_2b = var.private_subnet_id_2b

  airflow_alb_target_group_arn = module.alb.airflow_alb_tg
  ecs_airflow_container_port   = var.ecs_airflow_container_port
  sh_alb_target_group_arn      = module.alb.sh_alb_tg
  ecs_sh_container_port        = var.ecs_sh_container_port

  //Service Discovery
  scheduler_registry_arn    = module.service_discovery.scheduler_service_discovery
  webserver_registry_arn    = module.service_discovery.webserver_service_discovery
  go_app_registry_arn       = module.service_discovery.go_app_service_discovery
  triggerer_registry_arn    = module.service_discovery.triggerer_service_discovery
  sh_backend_registry_arn   = module.service_discovery.sh_backend_service_discovery
  sh_activemq_registry_arn  = module.service_discovery.sh_activemq_service_discovery
  internal_api_registry_arn = module.service_discovery.internal_api_service_discovery

  aws_region         = var.aws_region
  backend_account_id = var.backend_account_id
  backend_aws_region = var.backend_aws_region
  environment        = var.environment
}

module "webpage" {
  source = "./modules/webpage"

  environment     = var.environment
  sh_alb          = module.alb.sh_alb_dns_name
  zone_id         = local.sh_secrets.ZONE_ID
  domain_name     = var.domain_name
  aliases         = var.aliases
  certificate_arn = local.sh_secrets.CERTIFICATE_ARN
}