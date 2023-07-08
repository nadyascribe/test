output "sh_cloudfront_domain_name" {
  value = aws_cloudfront_distribution.s3_sh_distribution.domain_name
}

output "cloudfront_dist_id" {
  value = aws_cloudfront_distribution.s3_sh_distribution.id
}

output "website_address" {
  value = var.domain_name
}

output "s3_bucket_name" {
  value = aws_s3_bucket.webapp_sh_bucket.id
}

output "s3_default_bucket_name" {
  value = aws_s3_bucket.webapp_sh_default_bucket.id
}