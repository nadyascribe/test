terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.61"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.2.0"
    }
  }

  backend "s3" {
    bucket         = "scribe-airflow-terraform-state-bucket"
    dynamodb_table = "scribe-airflow-terraform-state-lock"
    key            = "scribe/terraform.tfstate"
    region         = "us-west-2"
    encrypt        = true
  }

  required_version = ">= 0.14.9"
}
