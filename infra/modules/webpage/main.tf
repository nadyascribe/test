locals {
  # acm_certs     = ["acm"]
  //CloudFront uses certificates from US-EAST-1 region only
  webapp_v2_origin_id = "webapp-v2"
  webapp_beta_origin_id = "webapp-beta"
  webapp_v1_origin_id = "webapp-v1"
  webapp_origin_id = "webapp-default"
  sh_alb_origin_id = "webapp-sh-alb"
}

resource "aws_s3_bucket" "webapp_sh_bucket" {
  bucket = "webapp-sh-${var.environment}"
  force_destroy = terraform.workspace=="test"?true:false
  tags = {
    Name        = "webapp-sh-v2-${var.environment}-bucket"
    Environment = "${var.environment}"
  }
}

resource "aws_s3_bucket" "webapp_sh_default_bucket" {
  bucket = "webapp-sh-${var.environment}-default"
  force_destroy = terraform.workspace=="test"?true:false
  tags = {
    Name        = "webapp-sh-${var.environment}-default-bucket"
    Environment = "${var.environment}"
  }
}

resource "aws_s3_bucket_acl" "sh_private_acl" {
  count = terraform.workspace=="test"?0:1
  bucket = aws_s3_bucket.webapp_sh_bucket.id
  acl    = "private"
}

resource "aws_s3_bucket_acl" "sh_default_private_acl" {
  count = terraform.workspace=="test"?0:1
  bucket = aws_s3_bucket.webapp_sh_default_bucket.id
  acl    = "private"
}

resource "aws_s3_bucket_public_access_block" "sh_block_public_access" {
  bucket = aws_s3_bucket.webapp_sh_bucket.id
  block_public_acls   = true
  block_public_policy = true
  ignore_public_acls  = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_public_access_block" "default_sh_block_public_access" {
  bucket = aws_s3_bucket.webapp_sh_default_bucket.id
  block_public_acls   = true
  block_public_policy = true
  ignore_public_acls  = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_policy" "s3_sh_bucket_policy" {
  bucket = aws_s3_bucket.webapp_sh_bucket.id
  policy = data.aws_iam_policy_document.sh_cf_s3_policy.json
}

data "aws_iam_policy_document" "sh_cf_s3_policy" {
  statement {
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.webapp_sh_bucket.arn}/*"]
    principals {
      type        = "AWS"
      identifiers = [aws_cloudfront_origin_access_identity.webapp_origin_access_identity.iam_arn]
    }
  }
}

resource "aws_s3_bucket_policy" "s3_default_sh_bucket_policy" {
  bucket = aws_s3_bucket.webapp_sh_default_bucket.id
  policy = data.aws_iam_policy_document.sh_default_cf_s3_policy.json
}

data "aws_iam_policy_document" "sh_default_cf_s3_policy" {
  statement {
    actions   = ["s3:GetObject"]
    resources = ["${aws_s3_bucket.webapp_sh_default_bucket.arn}/*"]
    principals {
      type        = "AWS"
      identifiers = [aws_cloudfront_origin_access_identity.webapp_origin_access_identity.iam_arn]
    }
  }
}

resource "aws_route53_record" "sh_route53_record" {
  depends_on = [
    aws_cloudfront_distribution.s3_sh_distribution
  ]

  zone_id = var.zone_id
  name    = var.domain_name
  type    = "CNAME"
  records = [aws_cloudfront_distribution.s3_sh_distribution.domain_name]
  ttl     = "5"
}

resource "aws_cloudfront_distribution" "s3_sh_distribution" {

  origin {
    domain_name = aws_s3_bucket.webapp_sh_default_bucket.bucket_regional_domain_name
    origin_id   = local.webapp_origin_id

    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.webapp_origin_access_identity.cloudfront_access_identity_path
    }
  }

  origin {
    domain_name = aws_s3_bucket.webapp_sh_default_bucket.bucket_regional_domain_name
    origin_id   = local.webapp_v1_origin_id

    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.webapp_origin_access_identity.cloudfront_access_identity_path
    }
  }

  origin {
    domain_name = aws_s3_bucket.webapp_sh_bucket.bucket_regional_domain_name
    origin_id = local.webapp_beta_origin_id

    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.webapp_origin_access_identity.cloudfront_access_identity_path
    }
  }
  
  origin {
    domain_name = aws_s3_bucket.webapp_sh_bucket.bucket_regional_domain_name
    origin_id   = local.webapp_v2_origin_id

    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.webapp_origin_access_identity.cloudfront_access_identity_path
    }
  }
  
  origin {
    domain_name = var.sh_alb
    origin_id   = local.sh_alb_origin_id
    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "http-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }

  enabled             = true
  is_ipv6_enabled     = true
  default_root_object = "index.html"

  aliases = var.aliases
  

  ordered_cache_behavior {
    path_pattern     = "/${var.sh_alb}/*"
    allowed_methods  = ["HEAD", "DELETE", "POST", "GET", "OPTIONS", "PUT", "PATCH"]
    cached_methods   = ["GET", "HEAD", "OPTIONS"]
    target_origin_id = local.sh_alb_origin_id

    forwarded_values {
      query_string = true
      headers      = ["Origin"]

      cookies {
        forward = "all"
      }
    }

    min_ttl                = 0
    default_ttl            = 86400
    max_ttl                = 31536000
    compress               = true
    viewer_protocol_policy = "allow-all"
  }

  ordered_cache_behavior {
    path_pattern     = "v2.0/*"
    allowed_methods  = ["HEAD", "GET"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = local.webapp_v2_origin_id

    forwarded_values {
      query_string = true
      headers      = ["Origin"]

      cookies {
        forward = "all"
      }
    }
    function_association {
      event_type = "viewer-request"
      function_arn = aws_cloudfront_function.v2AppRedirect.arn
    }

    min_ttl                = 0
    default_ttl            = 86400
    max_ttl                = 31536000
    compress               = true
    viewer_protocol_policy = "allow-all"
  }

  ordered_cache_behavior {
    path_pattern     = "v1.0/*"
    allowed_methods  = ["HEAD", "GET"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = local.webapp_v1_origin_id

    forwarded_values {
      query_string = true
      headers      = ["Origin"]

      cookies {
        forward = "all"
      }
    }
    function_association {
      event_type = "viewer-request"
      function_arn = aws_cloudfront_function.v1AppRedirect.arn
    }

    min_ttl                = 0
    default_ttl            = 86400
    max_ttl                = 31536000
    compress               = true
    viewer_protocol_policy = "allow-all"
  }

  ordered_cache_behavior {
    path_pattern     = "beta/*"
    allowed_methods  = ["HEAD", "GET"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = local.webapp_beta_origin_id

    forwarded_values {
      query_string = true
      headers      = ["Origin"]

      cookies {
        forward = "all"
      }
    }
    function_association {
      event_type = "viewer-request"
      function_arn = aws_cloudfront_function.betaAppRedirect.arn
    }

    min_ttl                = 0
    default_ttl            = 86400
    max_ttl                = 31536000
    compress               = true
    viewer_protocol_policy = "allow-all"
  }

  default_cache_behavior {
    allowed_methods = [
      "GET",
      "HEAD",
    ]

    cached_methods = [
      "GET",
      "HEAD",
    ]

    target_origin_id = local.webapp_origin_id

    forwarded_values {
      query_string = false

      cookies {
        forward = "none"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 86400
    max_ttl                = 31536000
  }

  price_class = var.price_class

  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  viewer_certificate {
    acm_certificate_arn      = var.certificate_arn
    ssl_support_method       = "sni-only"
    minimum_protocol_version = "TLSv1.2_2019"
  }

  custom_error_response {
    error_code            = 403
    response_code         = 200
    error_caching_min_ttl = 0
    response_page_path    = "/"
  }

  wait_for_deployment = false
  tags                = var.tags
}

resource "aws_cloudfront_origin_access_identity" "webapp_origin_access_identity" {
  comment = "access-identity-webapp-sh-${var.environment}.s3.amazonaws.com"
}

resource "aws_cloudfront_function" "v2AppRedirect" {
  name    = "${var.environment}-v2AppRedirect"
  runtime = "cloudfront-js-1.0"
  comment = "Redirects /v2.0/* requests to /v2.0/index.html"
  publish = true
  code    = file("${path.module}/functions/cloudfront_redirect_v2.js")
}

resource "aws_cloudfront_function" "betaAppRedirect" {
  name    = "${var.environment}-betaAppRedirect"
  runtime = "cloudfront-js-1.0"
  comment = "Redirects /beta/* requests to /beta/index.html"
  publish = true
  code    = file("${path.module}/functions/cloudfront_redirect_beta.js")
}

resource "aws_cloudfront_function" "v1AppRedirect" {
  name    = "${var.environment}-v1AppRedirect"
  runtime = "cloudfront-js-1.0"
  comment = "Redirects /v1.0/* requests to /v1.0/index.html"
  publish = true
  code    = file("${path.module}/functions/cloudfront_redirect_v1.js")
}  