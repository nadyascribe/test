variable "tags" {
  type        = map(string)
  default     = {}
  description = "tags for all the resources, if any"
}

variable "price_class" {
  default     = "PriceClass_100" // Only US,Canada,Europe
  description = "CloudFront distribution price class"
}

variable "sh_alb" {
  description = "ALB for backend ECS service"
}

variable "zone_id" {
  type = string
  description = "Route53 zone id"
}

variable "certificate_arn" {
  description = "ACM Certificate"
}

variable "aliases" {
  description = "alternate domain name"
}

variable "environment" {
  description = "A name to describe the environment we're creating."
}

variable "domain_name" {
  description = "name of domain"
}