# ---------------------------------------------------------------------------------------------------------------------
# RDS DB SUBNET GROUP
# ---------------------------------------------------------------------------------------------------------------------
resource "aws_db_subnet_group" "db-subnet-grp" {
  name        = "airflow-${var.environment}-db-subnet-group"
  description = "Airflow Database Subnet Group"
  subnet_ids  = var.private_subnet_ids
}

# ---------------------------------------------------------------------------------------------------------------------
# RDS (PostgreSQL)
# ---------------------------------------------------------------------------------------------------------------------

resource "aws_db_instance" "db" {
  identifier        = "scribe-${var.environment}-airflow"
  allocated_storage = 80
  deletion_protection = terraform.workspace=="test"?false:true
  backup_retention_period = 30
  apply_immediately = true
  engine            = "postgres"
  engine_version    = "13.7"
  port              = var.db_port
  instance_class    = var.db_instance_type
  name              = var.db_name
  username          = var.db_user
  password          = var.db_password
  vpc_security_group_ids = [aws_security_group.db-sg.id]
  multi_az               = false
  db_subnet_group_name   = aws_db_subnet_group.db-subnet-grp.id
  parameter_group_name   = "default.postgres13"
  publicly_accessible    = false
  skip_final_snapshot    = true

  tags = {
    Name = "${var.environment}-airflow-db"
  }
}

# ---------------------------------------------------------------------------------------------------------------------
# RDS (SECURITY GROUP)
# ---------------------------------------------------------------------------------------------------------------------

resource "aws_security_group" "db-sg" {
  name        = "airflow-${var.environment}-rds-sg"
  description = "airflow-security-group-db-instance"
  vpc_id      = var.vpc_id

  tags = {
    Name        = "${var.environment}-airflow-db-instance"
    Environment = var.environment
  }
}

resource "aws_security_group_rule" "airflow_rds_outbound" {
  type              = "egress"
  from_port         = 0
  to_port           = 0
  protocol          = "-1"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.db-sg.id
}

resource "aws_security_group_rule" "airflow_rds_inbound_one" {
  type              = "ingress"
  from_port         = 5432
  to_port           = 5432
  protocol          = "tcp"
  cidr_blocks       = [var.vpc_cidr]
  security_group_id = aws_security_group.db-sg.id
}

resource "aws_security_group_rule" "airflow_rds_inbound_two" {
  type              = "ingress"
  from_port         = 5432
  to_port           = 5432
  protocol          = "tcp"
  source_security_group_id = var.airflow-ecs-security-group
  security_group_id = aws_security_group.db-sg.id
}