# data "aws_service_discovery_dns_namespace" "airflow_service_discovery" {
#   name = "scribe-${var.environment}-app-sd"
#   type = "DNS_PRIVATE"
# }

resource "aws_service_discovery_service" "internal_api" {
  name = "internal-api"

  dns_config {
    namespace_id = var.sd_namespace_id

    dns_records {
      ttl  = 60
      type = "A"
    }

    routing_policy = "MULTIVALUE"
  }

  health_check_custom_config {
    failure_threshold = 1
}
}

resource "aws_service_discovery_service" "airflow_scheduler" {
  name = "scheduler-${var.environment}-airflow"

  dns_config {
    namespace_id = var.sd_namespace_id

    dns_records {
      ttl  = 60
      type = "A"
    }

    routing_policy = "MULTIVALUE"
  }

  health_check_custom_config {
    failure_threshold = 1
}
}

resource "aws_service_discovery_service" "airflow_webserver" {
  name = "webserver-airflow"

  dns_config {
    namespace_id = var.sd_namespace_id

    dns_records {
      ttl  = 60
      type = "A"
    }

    routing_policy = "MULTIVALUE"
  }

  health_check_custom_config {
    failure_threshold = 1
}
}

resource "aws_service_discovery_service" "airflow_go_app" {
  name = "go-app-${var.environment}-airflow"

  dns_config {
    namespace_id = var.sd_namespace_id

    dns_records {
      ttl  = 60
      type = "A"
    }

    routing_policy = "MULTIVALUE"
  }

  health_check_custom_config {
    failure_threshold = 1
}
}

resource "aws_service_discovery_service" "airflow_triggerer" {
  name = "triggerer-${var.environment}-airflow"

  dns_config {
    namespace_id = var.sd_namespace_id

    dns_records {
      ttl  = 60
      type = "A"
    }

    routing_policy = "MULTIVALUE"
  }

  health_check_custom_config {
    failure_threshold = 1
}
}

resource "aws_service_discovery_service" "sh_backend" {
  name = "sh-backend"

  dns_config {
    namespace_id = var.sd_namespace_id

    dns_records {
      ttl  = 60
      type = "A"
    }

    routing_policy = "MULTIVALUE"
  }

  health_check_custom_config {
    failure_threshold = 1
}
}

resource "aws_service_discovery_service" "sh_activemq" {
  name = "sh-activemq"

  dns_config {
    namespace_id = var.sd_namespace_id

    dns_records {
      ttl  = 60
      type = "A"
    }

    routing_policy = "MULTIVALUE"
  }

  health_check_custom_config {
    failure_threshold = 1
}
}