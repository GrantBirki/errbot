terraform {
  backend "remote" {
    organization = "errbot"

    workspaces {
      name = "errbot-aws"
    }
  }
  required_version = "= 1.1.0"
}

provider "aws" {
  region     = "us-west-2"
  access_key = var.AWS_ACCESS_KEY_ID
  secret_key = var.AWS_SECRET_ACCESS_KEY
}
