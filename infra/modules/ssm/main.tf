resource "aws_ssm_parameter" "scribe_environment" {
  name        = "/${var.environment}/airflow/SCRIBE_ENVIRONMENT"
  description = "Scribe environment name"
  type        = "SecureString"
  value       = var.environment

  tags = {
    environment = "${var.environment}"
  }
}

resource "aws_ssm_parameter" "scribe_almighty_fernet_key" {
  name        = "/${var.environment}/airflow/SCRIBE_ALMIGHTY_FERNET_KEY"
  description = "Scribe almighty fernet key"
  type        = "SecureString"
  value       = var.scribe_almighty_fernet_key

  tags = {
    environment = "${var.environment}"
  }
}

resource "aws_ssm_parameter" "slack_webhook_airflow_failures" {
  name        = "/${var.environment}/airflow/SLACK_WEBHOOK_AIRFLOW_FAILURES"
  description = "slack webhook airflow failures"
  type        = "SecureString"
  value       = var.slack_webhook_airflow_failures

  tags = {
    environment = "${var.environment}"
  }
}

resource "aws_ssm_parameter" "postgres_db" {
  name        = "/${var.environment}/airflow/POSTGRES_DB"
  description = "Airflow Postgres DB Name"
  type        = "SecureString"
  value       = var.db_name

  tags = {
    environment = "${var.environment}"
  }
}

resource "aws_ssm_parameter" "grype_path" {
  name        = "/${var.environment}/airflow/GRYPE_PATH"
  description = "Grype Path"
  type        = "SecureString"
  value       = var.grype_path

  tags = {
    environment = "${var.environment}"
  }
}

resource "aws_ssm_parameter" "scribe_service_bin_path" {
  name        = "/${var.environment}/airflow/SCRIBE_SERVICE_BIN_PATH"
  description = "Scribe service bin path"
  type        = "SecureString"
  value       = var.scribe_service_bin_path

  tags = {
    environment = "${var.environment}"
  }
}


resource "aws_ssm_parameter" "chainbench_bin_path" {
  name        = "/${var.environment}/airflow/CHAINBENCH_BIN_PATH"
  description = "Chainbench bin path"
  type        = "SecureString"
  value       = var.chainbench_bin_path

  tags = {
    environment = "${var.environment}"
  }
}

resource "aws_ssm_parameter" "shared_directory" {
  name        = "/${var.environment}/airflow/SHARED_DIRECTORY"
  description = "Shared directory"
  type        = "SecureString"
  value       = var.shared_directory

  tags = {
    environment = "${var.environment}"
  }
}

resource "aws_ssm_parameter" "github_posture_policy_path" {
  name        = "/${var.environment}/airflow/GITHUB_POSTURE_POLICY_PATH"
  description = "Github posture policy path"
  type        = "SecureString"
  value       = var.github_posture_policy_path

  tags = {
    environment = "${var.environment}"
  }
}

resource "aws_ssm_parameter" "gcs_package_version_to_project_source" {
  name        = "/${var.environment}/airflow/GCS_PACKAGE_VERSION"
  description = "GCS Package version"
  type        = "SecureString"
  value       = var.gcs_package_version_to_project_source

  tags = {
    environment = "${var.environment}"
  }
}

resource "aws_ssm_parameter" "sh_postgres_db" {
  name        = "/${var.environment}/sh-backend/POSTGRES_DB"
  description = "SH backend Postgres DB Name"
  type        = "SecureString"
  value       = var.sh_db_name

  tags = {
    environment = "${var.environment}"
  }
}

resource "aws_ssm_parameter" "postgres_host" {
  name        = "/${var.environment}/airflow/POSTGRES_HOST"
  description = "Airflow Postgres DB Host"
  type        = "SecureString"
  value       = var.db_host

  tags = {
    environment = "${var.environment}"
  }
}

resource "aws_ssm_parameter" "postgres_password" {
  name        = "/${var.environment}/airflow/POSTGRES_PASSWORD"
  description = "Airflow Postgres DB Password"
  type        = "SecureString"
  value       = var.db_password

  tags = {
    environment = "${var.environment}"
  }
}

resource "aws_ssm_parameter" "postgres_port" {
  name        = "/${var.environment}/airflow/POSTGRES_PORT"
  description = "Airflow Postgres DB Port"
  type        = "SecureString"
  value       = var.db_port

  tags = {
    environment = "${var.environment}"
  }
}

resource "aws_ssm_parameter" "postgres_user" {
  name        = "/${var.environment}/airflow/POSTGRES_USER"
  description = "Airflow Postgres DB User"
  type        = "SecureString"
  value       = var.db_user

  tags = {
    environment = "${var.environment}"
  }
}

resource "aws_ssm_parameter" "postgres_default_conn" {
  name        = "/${var.environment}/airflow/POSTGRES_DEFAULT_CONN"
  description = "Airflow Postgres Default Connection"
  type        = "SecureString"
  value       = "postgresql://${var.db_user}:${var.db_password}@${var.db_host}/${var.db_name}"

  tags = {
    environment = "${var.environment}"
  }
}

resource "aws_ssm_parameter" "github_default_conn" {
  name        = "/${var.environment}/airflow/GITHUB_DEFAULT_CONN"
  description = "Airflow Github Default Conn"
  type        = "SecureString"
  value       = "generic://${var.github_app_integration_id}:${var.github_app_private_key}@"

  tags = {
    environment = "${var.environment}"
  }
}

resource "aws_ssm_parameter" "s3_conn" {
  name        = "/${var.environment}/airflow/S3_CONN"
  description = "Airflow S3 Connection"
  type        = "SecureString"
  value       = var.s3_conn

  tags = {
    environment = "${var.environment}"
  }
}

resource "aws_ssm_parameter" "gcs_default_conn" {
  name        = "/${var.environment}/airflow/GCS_DEFAULT_CONN"
  description = "Airflow GCS Default Connection"
  type        = "SecureString"
  value       = var.gcs_default_conn

  tags = {
    environment = "${var.environment}"
  }
}

resource "aws_ssm_parameter" "airflow_uid" {
  name        = "/${var.environment}/airflow/AIRFLOW_UID"
  description = "Airflow UID"
  type        = "SecureString"
  value       = var.airflow_uid

  tags = {
    environment = "${var.environment}"
  }
}

resource "aws_ssm_parameter" "airflow_core_dags_paused_at_creation" {
  name        = "/${var.environment}/airflow/AIRFLOW__CORE__DAGS_ARE_PAUSED_AT_CREATION"
  description = "AIRFLOW CORE DAGS ARE PAUSED AT CREATION"
  type        = "SecureString"
  value       = var.airflow_core_dags_paused_at_creation

  tags = {
    environment = "${var.environment}"
  }
}

resource "aws_ssm_parameter" "airflow_core_executor" {
  name        = "/${var.environment}/airflow/AIRFLOW__CORE__EXECUTOR"
  description = "Airflow Core Executor"
  type        = "SecureString"
  value       = var.airflow_core_executor

  tags = {
    environment = "${var.environment}"
  }
}

resource "aws_ssm_parameter" "airflow_core_fernet_key" {
  name        = "/${var.environment}/airflow/AIRFLOW__CORE__FERNET_KEY"
  description = "AIRFLOW CORE FERNET KEY"
  type        = "SecureString"
  value       = var.airflow_core_fernet_key

  tags = {
    environment = "${var.environment}"
  }
}

resource "aws_ssm_parameter" "airflow_core_load_examples" {
  name        = "/${var.environment}/airflow/AIRFLOW__CORE__LOAD_EXAMPLES"
  description = "AIRFLOW CORE LOAD EXAMPLES"
  type        = "SecureString"
  value       = var.airflow_core_load_examples

  tags = {
    environment = "${var.environment}"
  }
}

resource "aws_ssm_parameter" "airflow_database_load_default_connections" {
  name        = "/${var.environment}/airflow/AIRFLOW__DATABASE__LOAD_DEFAULT_CONNECTIONS"
  description = "AIRFLOW DATABASE LOAD DEFAULT CONNECTIONS"
  type        = "SecureString"
  value       = var.airflow_database_load_default_connections

  tags = {
    environment = "${var.environment}"
  }
}

resource "aws_ssm_parameter" "airflow_database_sql_alchemy_conn" {
  name        = "/${var.environment}/airflow/AIRFLOW__DATABASE__SQL_ALCHEMY_CONN"
  description = "AIRFLOW DATABASE SQL ALCHEMY_CONN"
  type        = "SecureString"
  value       = "postgresql+psycopg2://${var.db_user}:${var.db_password}@${var.db_host}/${var.db_name}"

  tags = {
    environment = "${var.environment}"
  }
}

resource "aws_ssm_parameter" "sqlalchemy_silence_uber_warning" {
  name        = "/${var.environment}/airflow/SQLALCHEMY_SILENCE_UBER_WARNING"
  description = "SQLALCHEMY SILENCE UBER WARNING"
  type        = "SecureString"
  value       = var.sqlalchemy_silence_uber_warning

  tags = {
    environment = "${var.environment}"
  }
}

resource "aws_ssm_parameter" "airflow_db_upgrade" {
  name        = "/${var.environment}/airflow/_AIRFLOW_DB_UPGRADE"
  description = "AIRFLOW DB UPGRADE"
  type        = "SecureString"
  value       = var.airflow_db_upgrade

  tags = {
    environment = "${var.environment}"
  }
}

resource "aws_ssm_parameter" "airflow_www_user_create" {
  name        = "/${var.environment}/airflow/_AIRFLOW_WWW_USER_CREATE"
  description = "AIRFLOW WWW USER CREATE"
  type        = "SecureString"
  value       = var.airflow_www_user_create

  tags = {
    environment = "${var.environment}"
  }
}

resource "aws_ssm_parameter" "airflow_api_auth_backends" {
  name        = "/${var.environment}/airflow/AIRFLOW__API__AUTH_BACKENDS"
  description = "AIRFLOW API AUTH BACKENDS"
  type        = "SecureString"
  value       = var.airflow_api_auth_backends

  tags = {
    environment = "${var.environment}"
  }
}

resource "aws_ssm_parameter" "airflow_www_user_password" {
  name        = "/${var.environment}/airflow/_AIRFLOW_WWW_USER_PASSWORD"
  description = "AIRFLOW WWW USER PASSWORD"
  type        = "SecureString"
  value       = var.airflow_www_user_password

  tags = {
    environment = "${var.environment}"
  }
}

resource "aws_ssm_parameter" "airflow_www_username" {
  name        = "/${var.environment}/airflow/_AIRFLOW_WWW_USER_USERNAME"
  description = "AIRFLOW WWW USER USERNAME"
  type        = "SecureString"
  value       = var.airflow_www_username

  tags = {
    environment = "${var.environment}"
  }
}

resource "aws_ssm_parameter" "airflow_core_dagbag_import_error_traceback_depth" {
  name        = "/${var.environment}/airflow/AIRFLOW__CORE__DAGBAG_IMPORT_ERROR_TRACEBACK_DEPTH"
  description = "Airflow core dagbag import error traceback depth"
  type        = "SecureString"
  value       = var.airflow_core_dagbag_import_error_traceback_depth

  tags = {
    environment = "${var.environment}"
  }
}

resource "aws_ssm_parameter" "server_port" {
  name        = "/${var.environment}/sh-backend/SERVER_PORT"
  description = "server_port"
  type        = "SecureString"
  value       = var.server_port

  tags = {
    environment = "${var.environment}"
  }
}

resource "aws_ssm_parameter" "auth0_client_id" {
  name        = "/${var.environment}/sh-backend/AUTH0_CLIENT_ID"
  description = "auth0 client id"
  type        = "SecureString"
  value       = var.auth0_client_id

  tags = {
    environment = "${var.environment}"
  }
}

resource "aws_ssm_parameter" "auth0_client_secret" {
  name        = "/${var.environment}/sh-backend/AUTH0_CLIENT_SECRET"
  description = "auth0 client secret"
  type        = "SecureString"
  value       = var.auth0_client_secret

  tags = {
    environment = "${var.environment}"
  }
}

resource "aws_ssm_parameter" "sendgrid_api_key" {
  name        = "/${var.environment}/sh-backend/SENDGRID_API_KEY"
  description = "sendgrid api key"
  type        = "SecureString"
  value       = var.sendgrid_api_key

  tags = {
    environment = "${var.environment}"
  }
}

resource "aws_ssm_parameter" "scribe_hub_app_url" {
  name        = "/${var.environment}/sh-backend/SCRIBE_HUB_APP_URL"
  description = "scribe hub app url"
  type        = "SecureString"
  value       = var.scribe_hub_app_url

  tags = {
    environment = "${var.environment}"
  }
}

resource "aws_ssm_parameter" "mail_address_from" {
  name        = "/${var.environment}/sh-backend/MAIL_ADDRESS_FROM"
  description = "mail address from"
  type        = "SecureString"
  value       = var.mail_address_from

  tags = {
    environment = "${var.environment}"
  }
}

resource "aws_ssm_parameter" "auth0_audience" {
  name        = "/${var.environment}/sh-backend/AUTH0_AUDIENCE"
  description = "auth0 audience"
  type        = "SecureString"
  value       = var.auth0_audience

  tags = {
    environment = "${var.environment}"
  }
}

resource "aws_ssm_parameter" "auth0_domain" {
  name        = "/${var.environment}/sh-backend/AUTH0_DOMAIN"
  description = "auth0 domain"
  type        = "SecureString"
  value       = var.auth0_domain

  tags = {
    environment = "${var.environment}"
  }
}

resource "aws_ssm_parameter" "auth0_client_prefix" {
  name        = "/${var.environment}/sh-backend/AUTH0_CLIENT_PREFIX"
  description = "auth0 client prefix"
  type        = "SecureString"
  value       = var.auth0_client_prefix

  tags = {
    environment = "${var.environment}"
  }
}

resource "aws_ssm_parameter" "auth0_scribe_service_audience" {
  name        = "/${var.environment}/sh-backend/AUTH0_SCRIBE_SERVICE_AUDIENCE"
  description = "auth0 scribe service audience"
  type        = "SecureString"
  value       = var.auth0_scribe_service_audience

  tags = {
    environment = "${var.environment}"
  }
}

resource "aws_ssm_parameter" "auth0_redirect_token_secret" {
  name        = "/${var.environment}/sh-backend/AUTH0_REDIRECT_TOKEN_SECRET"
  description = "auth0 redirect token secret"
  type        = "SecureString"
  value       = var.auth0_redirect_token_secret

  tags = {
    environment = "${var.environment}"
  }
}

resource "aws_ssm_parameter" "mail_recipients_allowlist_enabled" {
  name        = "/${var.environment}/sh-backend/MAIL_RECIPIENTS_ALLOWLIST_ENABLED"
  description = "mail recipients allowlist enabled"
  type        = "SecureString"
  value       = tostring(var.mail_recipients_allowlist_enabled)

  tags = {
    environment = "${var.environment}"
  }
}

resource "aws_ssm_parameter" "statistics_spreadsheet_id" {
  name        = "/${var.environment}/sh-backend/STATISTICS_SPREADSHEET_ID"
  description = "statistics spreadsheet id"
  type        = "SecureString"
  value       = var.statistics_spreadsheet_id

  tags = {
    environment = "${var.environment}"
  }
}

resource "aws_ssm_parameter" "request_logging_include_query_string" {
  name        = "/${var.environment}/sh-backend/REQUEST_LOGGING_INCLUDE_QUERY_STRING"
  description = "request logging include query string"
  type        = "SecureString"
  value       = tostring(var.request_logging_include_query_string)

  tags = {
    environment = "${var.environment}"
  }
}

resource "aws_ssm_parameter" "request_logging_include_payload" {
  name        = "/${var.environment}/sh-backend/REQUEST_LOGGING_INCLUDE_PAYLOAD"
  description = "request logging include payload"
  type        = "SecureString"
  value       = tostring(var.request_logging_include_payload)

  tags = {
    environment = "${var.environment}"
  }
}

resource "aws_ssm_parameter" "scribe_api_base_uri" {
  name        = "/${var.environment}/sh-backend/SCRIBE_API_BASE_URI"
  description = "scribe api base uri"
  type        = "SecureString"
  value       = var.scribe_api_base_uri

  tags = {
    environment = "${var.environment}"
  }
}

resource "aws_ssm_parameter" "internal_api_password" {
  name        = "/${var.environment}/sh-backend/INTERNAL_API_PASSWORD"
  description = "internal api password"
  type        = "SecureString"
  value       = var.internal_api_password

  tags = {
    environment = "${var.environment}"
  }
}

resource "aws_ssm_parameter" "launchdarkly_sdk_key" {
  name        = "/${var.environment}/sh-backend/LAUNCHDARKLY_SDK_KEY"
  description = "launchdarkly sdk key"
  type        = "SecureString"
  value       = var.launchdarkly_sdk_key

  tags = {
    environment = "${var.environment}"
  }
}

resource "aws_ssm_parameter" "github_app_webhook_secret" {
  name        = "/${var.environment}/airflow/GITHUB_APP_WEBHOOK_SECRET"
  description = "GITHUB APP WEBHOOK SECRET"
  type        = "SecureString"
  value       = var.github_app_webhook_secret

  tags = {
    environment = "${var.environment}"
  }
}


resource "aws_ssm_parameter" "github_v3_api_url" {
  name        = "/${var.environment}/airflow/GITHUB_V3_API_URL"
  description = "GITHUB_V3_API_URL"
  type        = "SecureString"
  value       = var.github_v3_api_url

  tags = {
    environment = "${var.environment}"
  }
}


resource "aws_ssm_parameter" "github_integration_token_secret" {
  name        = "/${var.environment}/sh-backend/GITHUB_INTEGRATION_TOKEN_SECRET"
  description = "github integration token secret"
  type        = "SecureString"
  value       = var.github_integration_token_secret

  tags = {
    environment = "${var.environment}"
  }
}

resource "aws_ssm_parameter" "google_workload_identity_provider" {
  name        = "/${var.environment}/sh-backend/GOOGLE_WORKLOAD_IDENTITY_PROVIDER"
  description = "google workload identity provider"
  type        = "SecureString"
  value       = var.google_workload_identity_provider

  tags = {
    environment = "${var.environment}"
  }
}

resource "aws_ssm_parameter" "github_app_url" {
  name        = "/${var.environment}/sh-backend/GITHUB_APP_URL"
  description = "github app url"
  type        = "SecureString"
  value       = var.github_app_url

  tags = {
    environment = "${var.environment}"
  }
}

resource "aws_ssm_parameter" "bluesnap_webhook_allowed_ip_addresses" {
  name        = "/${var.environment}/sh-backend/BLUESNAP_WEBHOOK_ALLOWED_IP_ADDRESSES"
  description = "bluesnap webhook allowed ip addresses"
  type        = "SecureString"
  value       = var.bluesnap_webhook_allowed_ip_addresses

  tags = {
    environment = "${var.environment}"
  }
}

resource "aws_ssm_parameter" "inform_about_expired_plans_enabled" {
  name        = "/${var.environment}/sh-backend/INFORM_ABOUT_EXPIRED_PLANS_ENABLED"
  description = "Inform about expired plans enabled"
  type        = "SecureString"
  value       = var.inform_about_expired_plans_enabled

  tags = {
    environment = "${var.environment}"
  }
}

resource "aws_ssm_parameter" "inform_about_expired_plans_emails" {
  name        = "/${var.environment}/sh-backend/INFORM_ABOUT_EXPIRED_PLANS_EMAILS"
  description = "Inform about expired plans emails"
  type        = "SecureString"
  value       = var.inform_about_expired_plans_emails

  tags = {
    environment = "${var.environment}"
  }
}

resource "aws_ssm_parameter" "active_mq_enabled" {
  name        = "/${var.environment}/sh-backend/ACTIVE_MQ_ENABLED"
  description = "ActiveMQ Enabled"
  type        = "SecureString"
  value       = tostring(var.active_mq_enabled)

  tags = {
    environment = "${var.environment}"
  }
}

resource "aws_ssm_parameter" "active_mq_host" {
  name        = "/${var.environment}/sh-backend/ACTIVE_MQ_HOST"
  description = "ActiveMQ Host"
  type        = "SecureString"
  value       = var.active_mq_host

  tags = {
    environment = "${var.environment}"
  }
}

resource "aws_ssm_parameter" "activemq_username" {
  name        = "/${var.environment}/sh-backend/ACTIVE_MQ_USER"
  description = "ActiveMQ Username"
  type        = "SecureString"
  value       = var.active_mq_user

  tags = {
    environment = "${var.environment}"
  }
}

resource "aws_ssm_parameter" "activemq_password" {
  name        = "/${var.environment}/sh-backend/ACTIVE_MQ_PASSWORD"
  description = "ActiveMQ Password"
  type        = "SecureString"
  value       = var.activemq_password

  tags = {
    environment = "${var.environment}"
  }
}

resource "aws_ssm_parameter" "activemq_port" {
  name        = "/${var.environment}/sh-backend/ACTIVE_MQ_PORT"
  description = "ActiveMQ Port"
  type        = "SecureString"
  value       = var.active_mq_port

  tags = {
    environment = "${var.environment}"
  }
}


