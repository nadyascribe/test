# ---------------------------------------------------------------------------------------------------------------------
# ECS (Internal-API)
# ---------------------------------------------------------------------------------------------------------------------

resource "aws_ecs_service" "internal-api-ecs" {
  cluster = var.airflow_ecs_cluster
  task_definition = aws_ecs_task_definition.internal-api.arn
  desired_count = 1
  deployment_minimum_healthy_percent = 50
  enable_execute_command = true
  name = "internal-${var.environment}-api"
  launch_type     = "FARGATE"
  tags = {}
  tags_all = {}
  lifecycle {
    ignore_changes = [task_definition]
  }
   network_configuration {
    subnets = var.private_subnet_ids
    security_groups = ["${aws_security_group.airflow-ecs.id}"]
    assign_public_ip = false
  }
  service_registries {
    registry_arn = var.internal_api_registry_arn
  }
}

# ---------------------------------------------------------------------------------------------------------------------
# ECS (Airflow-Scheduler)
# ---------------------------------------------------------------------------------------------------------------------

resource "aws_ecs_service" "scheduler-airflow-ecs" {
  cluster = var.airflow_ecs_cluster
  task_definition = aws_ecs_task_definition.airflow-scheduler.arn
  desired_count = 1
  deployment_minimum_healthy_percent = 50
  enable_execute_command = true
  name = "airflow-${var.environment}-scheduler"
  launch_type     = "FARGATE"
  tags = {}
  tags_all = {}
  lifecycle {
    ignore_changes = [task_definition]
  }
   network_configuration {
    subnets = var.private_subnet_ids
    security_groups = ["${aws_security_group.airflow-ecs.id}"]
    assign_public_ip = false
  }
  service_registries {
    registry_arn = var.scheduler_registry_arn
  }
}

# ---------------------------------------------------------------------------------------------------------------------
# ECS (Airflow-Webserver)
# ---------------------------------------------------------------------------------------------------------------------

resource "aws_ecs_service" "webserver-airflow-ecs" {
  cluster = var.airflow_ecs_cluster
  task_definition = aws_ecs_task_definition.airflow-webserver.arn
  desired_count = 1
  deployment_minimum_healthy_percent = 50
  enable_execute_command = true
  name = "airflow-${var.environment}-webserver"
  launch_type     = "FARGATE"
  tags = {}
  tags_all = {}
  lifecycle {
    ignore_changes = [task_definition]
  }
  network_configuration {
    subnets = var.private_subnet_ids
    security_groups = ["${aws_security_group.airflow-ecs.id}"]
    assign_public_ip = false
  }
  service_registries {
    registry_arn = var.webserver_registry_arn
  }
}

# ---------------------------------------------------------------------------------------------------------------------
# ECS (Airflow-Triggerer)
# ---------------------------------------------------------------------------------------------------------------------

resource "aws_ecs_service" "triggerer-airflow-ecs" {
  cluster = var.airflow_ecs_cluster
  task_definition = aws_ecs_task_definition.airflow-triggerer.arn
  desired_count = 1
  deployment_minimum_healthy_percent = 50
  enable_execute_command = true
  name = "airflow-${var.environment}-triggerer"
  launch_type     = "FARGATE"
  tags = {}
  tags_all = {}
  lifecycle {
    ignore_changes = [task_definition]
  }
  network_configuration {
    subnets = var.private_subnet_ids
    security_groups = ["${aws_security_group.airflow-ecs.id}"]
    assign_public_ip = false
  }
  service_registries {
    registry_arn = var.triggerer_registry_arn
  }
}

# ---------------------------------------------------------------------------------------------------------------------
# ECS (Airflow-GoApp)
# ---------------------------------------------------------------------------------------------------------------------

resource "aws_ecs_service" "go-app-airflow-ecs" {
  cluster = var.airflow_ecs_cluster
  task_definition = aws_ecs_task_definition.airflow-go-app.arn
  desired_count = 1
  deployment_minimum_healthy_percent = 50
  enable_execute_command = true
  name = "airflow-${var.environment}-go-app"
  launch_type     = "FARGATE"
  tags = {}
  tags_all = {}
  lifecycle {
    ignore_changes = [task_definition]
  }
  load_balancer {
    container_name = "airflow-${var.environment}-go-app"
    container_port = var.ecs_airflow_container_port
    target_group_arn = var.airflow_alb_target_group_arn
  }
  network_configuration {
    subnets = var.private_subnet_ids
    security_groups = ["${aws_security_group.airflow-ecs.id}"]
    assign_public_ip = false
  }
  service_registries {
    registry_arn = var.go_app_registry_arn
  }
}
# ---------------------------------------------------------------------------------------------------------------------
# ECS Run Task (InitDB)
# ---------------------------------------------------------------------------------------------------------------------

resource "null_resource" "initdb_task_run" {
  depends_on = [
    aws_ecs_task_definition.airflow-db-init    // to make sure that you run task only after creating the task definition
  ]

  provisioner "local-exec" {
    command = <<EOF
    aws ecs run-task --cluster ${var.airflow_ecs_cluster} --task-definition airflow-${var.environment}-db-init --count 1 --launch-type FARGATE  --network-configuration awsvpcConfiguration={subnets=["${var.private_subnet_id_2a}","${var.private_subnet_id_2b}"],securityGroups=["${aws_security_group.airflow-ecs.id}"],assignPublicIp="DISABLED"}
    EOF
  }
}
# ---------------------------------------------------------------------------------------------------------------------
# ECS (SH-Backend)
# ---------------------------------------------------------------------------------------------------------------------

resource "aws_ecs_service" "sh-backend" {
  cluster = var.airflow_ecs_cluster
  task_definition = aws_ecs_task_definition.sh-backend.arn
  desired_count = 1
  deployment_minimum_healthy_percent = 50
  enable_execute_command = true
  name = "sh-${var.environment}-backend"
  launch_type     = "FARGATE"
  tags = {}
  tags_all = {}
  lifecycle {
    ignore_changes = [task_definition]
  }
  load_balancer {
    container_name = "sh-${var.environment}-backend"
    container_port = var.ecs_sh_container_port
    target_group_arn = var.sh_alb_target_group_arn
  }
  network_configuration {
    subnets = var.private_subnet_ids
    security_groups = ["${aws_security_group.airflow-ecs.id}"]
    assign_public_ip = false
  }
  service_registries {
    registry_arn = var.sh_backend_registry_arn
  }
}

# ---------------------------------------------------------------------------------------------------------------------
# ECS (SH-ActiveMQ)
# ---------------------------------------------------------------------------------------------------------------------

resource "aws_ecs_service" "sh-activemq" {
  cluster = var.airflow_ecs_cluster
  task_definition = aws_ecs_task_definition.sh-activemq.arn
  desired_count = 1
  deployment_minimum_healthy_percent = 50
  enable_execute_command = true
  name = "sh-${var.environment}-activemq"
  launch_type     = "FARGATE"
  tags = {}
  tags_all = {}
  lifecycle {
    ignore_changes = [task_definition]
  }
  network_configuration {
    subnets = var.private_subnet_ids
    security_groups = ["${aws_security_group.airflow-ecs.id}"]
    assign_public_ip = false
  }
  service_registries {
    registry_arn = var.sh_activemq_registry_arn
  }
}

resource "aws_security_group" "airflow-ecs" {
  name        = "${var.environment}-airflow-ecs-sg"
  vpc_id      = var.vpc_id

  tags = {
    Name  = "${var.environment}-airflow-ecs-sg"
  }
}

resource "aws_security_group_rule" "airflow_ecs_outbound" {
  type              = "egress"
  from_port         = 0
  to_port           = 0
  protocol          = "-1"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.airflow-ecs.id
}

resource "aws_security_group_rule" "airflow_ecs_inbound_one" {
  type              = "ingress"
  from_port         = 8161
  to_port           = 8161
  protocol          = "tcp"
  cidr_blocks       = [var.vpc_cidr]
  security_group_id = aws_security_group.airflow-ecs.id
}
 
resource "aws_security_group_rule" "airflow_ecs_inbound_two" {
  type              = "ingress"
  from_port         = 61616
  to_port           = 61616
  protocol          = "tcp"
  cidr_blocks       = [var.vpc_cidr]
  security_group_id = aws_security_group.airflow-ecs.id
}

resource "aws_security_group_rule" "airflow_ecs_inbound_three" {
  type              = "ingress"
  from_port         = 8080
  to_port           = 8080
  protocol          = "tcp"
  cidr_blocks       = [var.vpc_cidr]
  security_group_id = aws_security_group.airflow-ecs.id
}
 
resource "aws_security_group_rule" "airflow_ecs_inbound_four" {
  type              = "ingress"
  from_port         = 4000
  to_port           = 4000
  protocol          = "tcp"
  cidr_blocks       = [var.vpc_cidr]
  security_group_id = aws_security_group.airflow-ecs.id
}

resource "aws_security_group_rule" "airflow_ecs_inbound_five" {
  type              = "ingress"
  from_port         = 8739
  to_port           = 8739
  protocol          = "tcp"
  cidr_blocks       = [var.vpc_cidr]
  security_group_id = aws_security_group.airflow-ecs.id
}
 
resource "aws_security_group_rule" "airflow_ecs_inbound_six" {
  type              = "ingress"
  from_port         = 5432
  to_port           = 5432
  protocol          = "tcp"
  cidr_blocks       = [var.vpc_cidr]
  security_group_id = aws_security_group.airflow-ecs.id
}

resource "aws_security_group_rule" "airflow_ecs_inbound_seven" {
  type              = "ingress"
  from_port         = 80
  to_port           = 80
  protocol          = "tcp"
  cidr_blocks       = [var.vpc_cidr]
  security_group_id = aws_security_group.airflow-ecs.id
}

resource "aws_security_group_rule" "airflow_ecs_inbound_eight" {
  type              = "ingress"
  from_port         = 1111
  to_port           = 1111
  protocol          = "tcp"
  cidr_blocks       = [var.vpc_cidr]
  security_group_id = aws_security_group.airflow-ecs.id
}

resource "aws_cloudwatch_log_group" "scheduler_container_log_group" {
  name = "/ecs/airflow-${var.environment}-scheduler"
  retention_in_days = 30
  tags = {
    Environment = var.environment
  }
}

resource "aws_cloudwatch_log_group" "webserver_container_log_group" {
  name = "/ecs/airflow-${var.environment}-webserver"
  retention_in_days = 30
  tags = {
    Environment = var.environment
  }
}

resource "aws_cloudwatch_log_group" "alembic_container_log_group" {
  name = "/ecs/airflow-${var.environment}-alembic"
  retention_in_days = 30
  tags = {
    Environment = var.environment
  }
}

resource "aws_cloudwatch_log_group" "triggerer_container_log_group" {
  name = "/ecs/airflow-${var.environment}-triggerer"
  retention_in_days = 30
  tags = {
    Environment = var.environment
  }
}

resource "aws_cloudwatch_log_group" "go_app_container_log_group" {
  name = "/ecs/airflow-${var.environment}-go-app"
  retention_in_days = 30
  tags = {
    Environment = var.environment
  }
}

resource "aws_cloudwatch_log_group" "db_init_container_log_group" {
  name = "/ecs/airflow-${var.environment}-db-init"
  retention_in_days = 30
  tags = {
    Environment = var.environment
  }
}

resource "aws_cloudwatch_log_group" "backend_container_log_group" {
  name = "/ecs/sh-${var.environment}-backend"
  retention_in_days = 30
  tags = {
    Environment = var.environment
  }
}

resource "aws_cloudwatch_log_group" "activemq_container_log_group" {
  name = "/ecs/sh-${var.environment}-activemq"
  retention_in_days = 30
  tags = {
    Environment = var.environment
  }
}

resource "aws_cloudwatch_log_group" "internal_api_container_log_group" {
  name = "/ecs/sh-internal-${var.environment}-api"
  retention_in_days = 30
  tags = {
    Environment = var.environment
  }
}

# ---------------------------------------------------------------------------------------------------------------------
# EFS 
# ---------------------------------------------------------------------------------------------------------------------

resource "aws_efs_file_system" "scribe2_efs" {
  encrypted = true
  tags = {
    Name = "scribe2-${var.environment}-airflow-efs"
  }
}

resource "aws_efs_backup_policy" "policy" {
  file_system_id = aws_efs_file_system.scribe2_efs.id
  backup_policy {
    status = "ENABLED"
  }
}

# Creating the EFS access point for AWS EFS File system
resource "aws_efs_access_point" "sh-airflow-efs" {
  file_system_id = aws_efs_file_system.scribe2_efs.id
}

resource "aws_efs_mount_target" "airflow-efs-mount-2a" {
  file_system_id = aws_efs_file_system.scribe2_efs.id
  subnet_id      = var.private_subnet_id_2a
  security_groups = ["${aws_security_group.ingress-efs.id}"]
}

resource "aws_efs_mount_target" "airflow-efs-mount-2b" {
  file_system_id = aws_efs_file_system.scribe2_efs.id
  subnet_id      = var.private_subnet_id_2b
  security_groups = ["${aws_security_group.ingress-efs.id}"]
}

resource "aws_security_group" "ingress-efs" {
   name = "airflow-ingress-${var.environment}-efs-sg"
   vpc_id = var.vpc_id

   // NFS
   ingress {
     security_groups = ["${aws_security_group.airflow-ecs.id}"]
     from_port = 2049
     to_port = 2049
     protocol = "tcp"
   }

   // Terraform removes the default rule
   egress {
     security_groups = ["${aws_security_group.airflow-ecs.id}"]
     from_port = 0
     to_port = 0
     protocol = "-1"
   }
 }

# ---------------------------------------------------------------------------------------------------------------------
# ECS Task Definition (Internal-API)
# ---------------------------------------------------------------------------------------------------------------------
data "template_file" "internal-api" {
  template = "${file("${path.module}/templates/internal-api.json.tpl")}"
  vars = {
    environment         = var.environment
    aws_region          = var.aws_region
    account_id          = var.account_id
    awslogs-group       = aws_cloudwatch_log_group.internal_api_container_log_group.name
  }
}

resource aws_ecs_task_definition "internal-api" {
  family                   = "internal-${var.environment}-api"
  network_mode             = var.network_mode
  requires_compatibilities = ["FARGATE"]
  cpu                      = 2048
  memory                   = 4096
  execution_role_arn       = "arn:aws:iam::${var.account_id}:role/ecsTaskExecutionRole"
  task_role_arn            = "arn:aws:iam::${var.account_id}:role/ecsTaskExecutionRole"
  container_definitions = data.template_file.internal-api.rendered
}  

# ---------------------------------------------------------------------------------------------------------------------
# ECS Task Definition (Airflow-Scheduler)
# ---------------------------------------------------------------------------------------------------------------------
data "template_file" "airflow-scheduler" {
  template = "${file("${path.module}/templates/airflow-scheduler.json.tpl")}"
  vars = {
    environment         = var.environment
    aws_region          = var.aws_region
    account_id          = var.account_id
    awslogs-group       = aws_cloudwatch_log_group.scheduler_container_log_group.name
  }
}

resource aws_ecs_task_definition "airflow-scheduler" {
  family                   = "airflow-${var.environment}-scheduler"
  network_mode             = var.network_mode
  requires_compatibilities = ["FARGATE"]
  cpu                      = 2048
  memory                   = 4096
  execution_role_arn       = "arn:aws:iam::${var.account_id}:role/ecsTaskExecutionRole"
  task_role_arn            = "arn:aws:iam::${var.account_id}:role/ecsTaskExecutionRole"
  container_definitions = data.template_file.airflow-scheduler.rendered
  volume {
    name      = "airflow-logs"
    efs_volume_configuration {
      file_system_id = aws_efs_file_system.scribe2_efs.id
      root_directory = "/"
    }
  }
}  

# ---------------------------------------------------------------------------------------------------------------------
# ECS Task Definition (Airflow-alembic)
# ---------------------------------------------------------------------------------------------------------------------
data "template_file" "airflow-alembic" {
  template = "${file("${path.module}/templates/airflow-alembic.json.tpl")}"
  vars = {
    environment         = var.environment
    aws_region          = var.aws_region
    account_id          = var.account_id
    awslogs-group       = aws_cloudwatch_log_group.alembic_container_log_group.name
  }
}

resource aws_ecs_task_definition "airflow-alembic" {
  family                   = "airflow-${var.environment}-alembic"
  network_mode             = var.network_mode
  requires_compatibilities = ["FARGATE"]
  cpu                      = 1024
  memory                   = 2048
  execution_role_arn       = "arn:aws:iam::${var.account_id}:role/ecsTaskExecutionRole"
  task_role_arn            = "arn:aws:iam::${var.account_id}:role/ecsTaskExecutionRole"
  container_definitions    = data.template_file.airflow-alembic.rendered
}

# ---------------------------------------------------------------------------------------------------------------------
# ECS Task Definition (Airflow-Webserver)
# ---------------------------------------------------------------------------------------------------------------------
data "template_file" "airflow-webserver" {
  template = "${file("${path.module}/templates/airflow-webserver.json.tpl")}"
  vars = {
    environment         = var.environment
    aws_region          = var.aws_region
    account_id          = var.account_id
    awslogs-group       = aws_cloudwatch_log_group.webserver_container_log_group.name
  }
}

resource aws_ecs_task_definition "airflow-webserver" {
  family                   = "airflow-${var.environment}-webserver"
  network_mode             = var.network_mode
  requires_compatibilities = ["FARGATE"]
  cpu                      = 1024
  memory                   = 2048
  execution_role_arn       = "arn:aws:iam::${var.account_id}:role/ecsTaskExecutionRole"
  task_role_arn            = "arn:aws:iam::${var.account_id}:role/ecsTaskExecutionRole"
  container_definitions = data.template_file.airflow-webserver.rendered
  volume {
    name      = "airflow-logs"
    efs_volume_configuration {
      file_system_id = aws_efs_file_system.scribe2_efs.id
      root_directory = "/"
    }
  }
}

# ---------------------------------------------------------------------------------------------------------------------
# ECS Task Definition (Airflow-Triggerer)
# ---------------------------------------------------------------------------------------------------------------------
data "template_file" "airflow-triggerer" {
  template = "${file("${path.module}/templates/airflow-triggerer.json.tpl")}"
  vars = {
    environment         = var.environment
    aws_region          = var.aws_region
    account_id          = var.account_id
    awslogs-group       = aws_cloudwatch_log_group.triggerer_container_log_group.name
  }
}

resource aws_ecs_task_definition "airflow-triggerer" {
  family                   = "airflow-${var.environment}-triggerer"
  network_mode             = var.network_mode
  requires_compatibilities = ["FARGATE"]
  cpu                      = 2048
  memory                   = 4096
  execution_role_arn       = "arn:aws:iam::${var.account_id}:role/ecsTaskExecutionRole"
  task_role_arn            = "arn:aws:iam::${var.account_id}:role/ecsTaskExecutionRole"
  container_definitions = data.template_file.airflow-triggerer.rendered
  volume {
    name      = "airflow-logs"
    efs_volume_configuration {
      file_system_id = aws_efs_file_system.scribe2_efs.id
      root_directory = "/"
    }
  }
}

# ---------------------------------------------------------------------------------------------------------------------
# ECS Task Definition (Airflow-Go-App)
# ---------------------------------------------------------------------------------------------------------------------
data "template_file" "airflow-go-app" {
  template = "${file("${path.module}/templates/airflow-go-app.json.tpl")}"
  vars = {
    environment         = var.environment
    aws_region          = var.aws_region
    account_id          = var.account_id
    awslogs-group       = aws_cloudwatch_log_group.go_app_container_log_group.name
  }
}

resource aws_ecs_task_definition "airflow-go-app" {
  family                   = "airflow-${var.environment}-go-app"
  network_mode             = var.network_mode
  requires_compatibilities = ["FARGATE"]
  cpu                      = 512
  memory                   = 1024
  execution_role_arn       = "arn:aws:iam::${var.account_id}:role/ecsTaskExecutionRole"
  task_role_arn            = "arn:aws:iam::${var.account_id}:role/ecsTaskExecutionRole"
  container_definitions = data.template_file.airflow-go-app.rendered
  volume {
    name      = "airflow-logs"
    efs_volume_configuration {
      file_system_id = aws_efs_file_system.scribe2_efs.id
      root_directory = "/"
    }
  }
}

# ---------------------------------------------------------------------------------------------------------------------
# ECS Task Definition (SH-ActiveMQ)
# ---------------------------------------------------------------------------------------------------------------------
data "template_file" "sh-activemq" {
  template = "${file("${path.module}/templates/sh-activemq.json.tpl")}"
  vars = {
    environment         = var.environment
    aws_region          = var.aws_region
    account_id          = var.account_id
    awslogs-group       = aws_cloudwatch_log_group.activemq_container_log_group.name
    backend_aws_region  = var.backend_aws_region
    backend_account_id  = var.backend_account_id
  }
}

resource aws_ecs_task_definition "sh-activemq" {
  family                   = "sh-${var.environment}-activemq"
  network_mode             = var.network_mode
  requires_compatibilities = ["FARGATE"]
  cpu                      = 512
  memory                   = 1024
  execution_role_arn       = "arn:aws:iam::${var.account_id}:role/ecsTaskExecutionRole"
  task_role_arn            = "arn:aws:iam::${var.account_id}:role/ecsTaskExecutionRole"
  container_definitions = data.template_file.sh-activemq.rendered
}


# ---------------------------------------------------------------------------------------------------------------------
# ECS Task Definition (SH-Backend)
# ---------------------------------------------------------------------------------------------------------------------
data "template_file" "sh-backend" {
  template = "${file("${path.module}/templates/sh-backend.json.tpl")}"
  vars = {
    environment         = var.environment
    aws_region          = var.aws_region
    account_id          = var.account_id
    awslogs-group       = aws_cloudwatch_log_group.backend_container_log_group.name
    backend_aws_region  = var.backend_aws_region
    backend_account_id  = var.backend_account_id
  }
}

resource aws_ecs_task_definition "sh-backend" {
  family                   = "sh-${var.environment}-backend"
  network_mode             = var.network_mode
  requires_compatibilities = ["FARGATE"]
  cpu                      = 2048
  memory                   = 4096
  execution_role_arn       = "arn:aws:iam::${var.account_id}:role/ecsTaskExecutionRole"
  task_role_arn            = "arn:aws:iam::${var.account_id}:role/ecsTaskExecutionRole"
  container_definitions = data.template_file.sh-backend.rendered
}

# ---------------------------------------------------------------------------------------------------------------------
# ECS Task Definition (Airflow-DB-Init)
# ---------------------------------------------------------------------------------------------------------------------
data "template_file" "airflow-db-init" {
  template = "${file("${path.module}/templates/airflow-db-init.json.tpl")}"
  vars = {
    environment         = var.environment
    aws_region          = var.aws_region
    account_id          = var.account_id
    awslogs-group       = aws_cloudwatch_log_group.db_init_container_log_group.name
    postgres_host_arn   = var.postgres_host_arn
  }
}

resource aws_ecs_task_definition "airflow-db-init" {
  family                   = "airflow-${var.environment}-db-init"
  network_mode             = var.network_mode
  requires_compatibilities = ["FARGATE"]
  cpu                      = 1024
  memory                   = 2048
  execution_role_arn       = "arn:aws:iam::${var.account_id}:role/ecsTaskExecutionRole"
  task_role_arn            = "arn:aws:iam::${var.account_id}:role/ecsTaskExecutionRole"
  container_definitions = data.template_file.airflow-db-init.rendered
}