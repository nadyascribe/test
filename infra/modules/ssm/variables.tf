variable "environment" {
  description = "The name of the environment"
}

variable "db_name" {
  description = "Airflow Postgres DB Name"
}

variable "sh_db_name" {
  description = "SH backend Postgres DB Name"
}

variable "db_host" {
  description = "Airflow Postgres DB Host"
}

variable "db_password" {
  description = "Airflow Postgres DB Password"
}

variable "db_port" {
  description = "Airflow Postgres DB Port"
}

variable "db_user" {
  description = "Airflow Postgres DB User"
}

variable "airflow_uid" {
  description = "Airflow UID"
}

variable "github_app_integration_id" {
  description = "Github App Integration ID"
}

variable "github_v3_api_url" {
  description = "github v3 api url"
}

variable "slack_webhook_airflow_failures" {
  description = "slack_webhook_airflow_failures"
}

variable "github_app_webhook_secret" {
  description = "github app webhook secret"
}

variable "github_app_private_key" {
  description = "Github App Private Key"
}

variable "airflow_core_dags_paused_at_creation" {
  description = "AIRFLOW CORE DAGS ARE PAUSED AT CREATION"
}

variable "airflow_core_executor" {
  description = "Airflow Core Executor"
}

variable "airflow_core_fernet_key" {
  description = "AIRFLOW CORE FERNET KEY"
}

variable "airflow_core_load_examples" {
  description = "AIRFLOW CORE LOAD EXAMPLES"
}

variable "airflow_database_load_default_connections" {
  description = "AIRFLOW DATABASE LOAD DEFAULT CONNECTIONS"
}

variable "scribe_almighty_fernet_key" {
  description = "Scribe almighty fernet key"
}

variable "s3_conn" {
  description = "Airflow S3 Connection"
}

variable "gcs_default_conn" {
  description = "Airflow GCS Default Connection"
}

variable "sqlalchemy_silence_uber_warning" {
  description = "SQLALCHEMY SILENCE UBER WARNING"
}

variable "auth0_client_id" {
  description = "auth0 client id"
}

variable "auth0_client_secret" {
  description = "auth0 client secret"
}

variable "sendgrid_api_key" {
  description = "sendgrid api key"
}

variable "auth0_redirect_token_secret" {
  description = "auth0 redirect token secret"
}

variable "scribe_hub_app_url" {
  description = "scribe hub app url"
}

variable "launchdarkly_sdk_key" {
  description = "launchdarkly sdk key"
}

variable "internal_api_password" {
  description = "internal api password"
}

variable "github_integration_token_secret" {
  description = "github integration token secret"
}

variable "activemq_password" {
  description = "ActiveMQ Password"
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

variable "airflow_www_user_password" {
  description = "AIRFLOW WWW USER PASSWORD"
}

variable "airflow_www_username" {
  description = "AIRFLOW WWW USER USERNAME"
}

variable "airflow_core_dagbag_import_error_traceback_depth" {
  description = "Airflow core dagbag import error traceback depth"
}

variable "auth0_audience" {
  type = string
}

variable "auth0_domain" {
  type = string
}

variable "auth0_client_prefix" {
  type = string
}

variable "auth0_scribe_service_audience" {
  type = string
}

variable "mail_recipients_allowlist_enabled" {
  default     = true
  description = "Allow sending emails to the domain other than 7bulls.com and scribe.com"
}

variable "statistics_spreadsheet_id" {
  description = "Domain of Auth0 service to authenticate"
}

variable "request_logging_include_query_string" {
  default     = true
  description = "Logging of the querystrings"
}

variable "request_logging_include_payload" {
  description = "Logging of the payloads"
}

variable "scribe_api_base_uri" {
  description = "Base uri for scribe api. Used for integration with the external scribe api"
}

variable "google_workload_identity_provider" {
  description = "Provider used to authentication in google sheets"
}

variable "github_app_url" {
  description = "Base uri for scribe github app backend. Used for registration of github app installation."
}

variable "bluesnap_webhook_allowed_ip_addresses" {
  description = "IP addresses allowed to call the BlueSnap webhook."
}

variable "inform_about_expired_plans_enabled" {
  description = "Enable sending notifications on team plan subscription expiry."
}

variable "inform_about_expired_plans_emails" {
  description = "Emails for sending notifications on team plan subscription expiry."
}

variable "active_mq_enabled" {
  default     = true
  description = "Use ActiveMQ for websocket connections"
}

variable "active_mq_user" {
  description = "ActiveMQ username"
}

variable "active_mq_host" {
  type = string
}

variable "server_port" {
  type = string
}

variable "mail_address_from" {
  type = string
}

variable "active_mq_port" {
  type = string
}

variable "grype_path" {
  description = "Grype Path"
}

variable "scribe_service_bin_path" {
  description = "Scribe Service Bin Path"
}

variable "chainbench_bin_path" {
    description = "Chainbench Bin Path"
}

variable "github_posture_policy_path" {
  description = "Github Posture Policy Path"
}

variable "shared_directory" {
  description = "Shared directory"
}

variable "gcs_package_version_to_project_source" {
  description = "GCS Package version"
}