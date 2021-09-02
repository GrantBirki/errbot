terraform {
  backend "remote" {
    organization = "errbot"

    workspaces {
      name = "errbot-containers"
    }
  }
}

provider "aws" {
  region = "us-west-2"
}

module "dynamodb_table" {
  source   = "terraform-aws-modules/dynamodb-table/aws"
  version = "1.1.0"

  name     = "remember"
  hash_key = "discord_server_id"
  range_key = "rem_key"
  billing_mode = "PAY_PER_REQUEST"
  point_in_time_recovery_enabled = true

  attributes = [
    {
      name = "discord_server_id"
      type = "N"
    },
    {
      name = "rem_key"
      type = "S"
    }
  ]

  tags = {
    managed_by = "terraform"
  }
}

# Configure the Microsoft Azure Provider
provider "azurerm" {
  features {}
  # Ignore Auth Warnings
  skip_provider_registration = true

  client_secret   = var.CLIENT_SECRET
  client_id       = var.CLIENT_ID
  tenant_id       = var.TENANT_ID
  subscription_id = var.SUBSCRIPTION_ID
}

module "errbot_container" {
  source = "./modules/container"

  # Bot Creds
  CHAT_SERVICE_TOKEN    = var.CHAT_SERVICE_TOKEN
  AWS_ACCESS_KEY_ID     = var.AWS_ACCESS_KEY_ID
  AWS_SECRET_ACCESS_KEY = var.AWS_SECRET_ACCESS_KEY

  # Bot Config
  COMMIT_SHA            = var.COMMIT_SHA
  BACKEND               = var.BACKEND
  BOT_PREFIX            = var.BOT_PREFIX
  BOT_ADMINS            = var.BOT_ADMINS
  BOT_EXTRA_BACKEND_DIR = var.BOT_EXTRA_BACKEND_DIR
  RIOT_TOKEN            = var.RIOT_TOKEN
  RIOT_REGION           = var.RIOT_REGION
  COSMOS_ACCOUNT_HOST   = var.COSMOS_ACCOUNT_HOST
  COSMOS_DATABASE       = var.COSMOS_DATABASE
  COSMOS_CONTAINER      = var.COSMOS_CONTAINER
  COSMOS_ACCOUNT_KEY    = var.COSMOS_ACCOUNT_KEY

  # Project Variables
  azure_resource_group = "errbot"
  project_name         = "errbot"
  azure_location       = "West US 2"

  commands = []

  # Container Resources
  cpu         = 2
  memory      = 2
  project_env = "prod"
  image_tag   = var.IMAGE_TAG
}
