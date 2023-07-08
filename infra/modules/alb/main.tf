# ---------------------------------------------------------------------------------------------------------------------
# LOAD BALANCER (SH-Airflow)
# ---------------------------------------------------------------------------------------------------------------------
resource "aws_alb" "airflow-alb" {
  name            = "sh-airflow-${var.environment}-alb"
  subnets         = var.public_subnet_ids
  security_groups = [aws_security_group.airflow-alb-sg.id]
  tags = {
    Environment = var.environment
  }
}

resource "aws_alb_target_group" "airflow-alb-tg" {
  name                 = "sh-airflow-${var.environment}-alb-tg"
  port                 = 80
  protocol             = "HTTP"
  target_type = "ip"
  vpc_id               = var.vpc_id
  deregistration_delay = var.deregistration_delay

  health_check {
    path     = var.airflow_health_check_path
    protocol = "HTTP"
    interval = 60
    timeout = 30
    healthy_threshold = 5
    unhealthy_threshold = 5
  }

  tags = {
    Environment = var.environment
  }
}

resource "aws_alb_listener" "airflow_http" {
  load_balancer_arn = aws_alb.airflow-alb.id
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type = "redirect"
    redirect {
      status_code = "HTTP_301"
      port        = "443"
      protocol    = "HTTPS"
    }
  }
}

resource "aws_alb_listener" "airflow_listener_ssl" {
  load_balancer_arn = aws_alb.airflow-alb.id
  port              = "443"
  protocol          = "HTTPS"
  depends_on        = [aws_alb_target_group.airflow-alb-tg]
  certificate_arn   = var.alb_certificate_arn 
  default_action {
    target_group_arn = aws_alb_target_group.airflow-alb-tg.id
    type             = "forward"
  }
}

resource "aws_security_group" "airflow-alb-sg" {
  name   = "sh-airflow-${var.environment}-alb-sg"
  vpc_id = var.vpc_id

  tags = {
    Environment = var.environment
  }
}

resource "aws_security_group_rule" "airflow_http_from_anywhere" {
  type              = "ingress"
  from_port         = 80
  to_port           = 80
  protocol          = "TCP"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.airflow-alb-sg.id
}

resource "aws_security_group_rule" "airflow_https_from_anywhere" {
  type              = "ingress"
  from_port         = 443
  to_port           = 443
  protocol          = "TCP"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.airflow-alb-sg.id
}

resource "aws_security_group_rule" "airflow_outbound_internet_access" {
  type              = "egress"
  from_port         = 0
  to_port           = 0
  protocol          = "-1"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.airflow-alb-sg.id
}

resource "aws_route53_record" "airflow_route53_record" {
  depends_on = [
    aws_alb.airflow-alb
  ]

  zone_id = var.zone_id
  name    = "airflow"
  type    = "A"

    alias {
      name    = aws_alb.airflow-alb.dns_name
      zone_id = aws_alb.airflow-alb.zone_id
      evaluate_target_health = true
    }
}

# ---------------------------------------------------------------------------------------------------------------------
# LOAD BALANCER (SH-Backend)
# ---------------------------------------------------------------------------------------------------------------------

resource "aws_alb" "sh-alb" {
  name            = "sh-${var.environment}-alb"
  subnets         = var.public_subnet_ids
  security_groups = [aws_security_group.sh-alb-sg.id]

  tags = {
    Environment = var.environment
  }
}

resource "aws_alb_target_group" "sh-alb-tg" {
  name                 = "sh-${var.environment}-alb-tg"
  port                 = 80
  protocol             = "HTTP"
  vpc_id               = var.vpc_id
  target_type = "ip"
  deregistration_delay = var.deregistration_delay

  health_check {
    path     = var.sh_health_check_path
    protocol = "HTTP"
    interval = 60
    timeout = 30
    healthy_threshold = 5
    unhealthy_threshold = 5
  }

  tags = {
    Environment = var.environment
  }
}

resource "aws_alb_listener" "sh_http" {
  load_balancer_arn = aws_alb.sh-alb.id
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type = "redirect"
    redirect {
      status_code = "HTTP_301"
      port        = "443"
      protocol    = "HTTPS"
    }
  }
}

resource "aws_alb_listener" "sh_listener_ssl" {
  load_balancer_arn = aws_alb.sh-alb.id
  port              = "443"
  protocol          = "HTTPS"
  depends_on        = [aws_alb_target_group.sh-alb-tg]
  certificate_arn   = var.alb_certificate_arn
  default_action {
    target_group_arn = aws_alb_target_group.sh-alb-tg.id
    type             = "forward"
  }
}

resource "aws_security_group" "sh-alb-sg" {
  name   = "sh-${var.environment}-alb-sg"
  vpc_id = var.vpc_id

  tags = {
    Environment = var.environment
  }
}

resource "aws_security_group_rule" "sh_http_from_anywhere" {
  type              = "ingress"
  from_port         = 80
  to_port           = 80
  protocol          = "TCP"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.sh-alb-sg.id
}

resource "aws_security_group_rule" "sh_https_from_anywhere" {
  type              = "ingress"
  from_port         = 443
  to_port           = 443
  protocol          = "TCP"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.sh-alb-sg.id
}

resource "aws_security_group_rule" "sh_outbound_internet_access" {
  type              = "egress"
  from_port         = 0
  to_port           = 0
  protocol          = "-1"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.sh-alb-sg.id
}

resource "aws_route53_record" "sh_route53_record" {
  depends_on = [
    aws_alb.sh-alb
  ]

  zone_id = var.zone_id
  name    = "sh"
  type    = "A"

    alias {
      name    = aws_alb.sh-alb.dns_name
      zone_id = aws_alb.sh-alb.zone_id
      evaluate_target_health = true
    }
}