terraform {
  backend "remote" {
    organization = "errbot"

    workspaces {
      name = "errbot-containers"
    }
  }
}

provider "aws" {
  region     = "us-west-2"
  access_key = var.AWS_ACCESS_KEY_ID
  secret_key = var.AWS_SECRET_ACCESS_KEY
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
  SPOTIFY_CLIENT_ID     = var.SPOTIFY_CLIENT_ID
  SPOTIFY_CLIENT_SECRET = var.SPOTIFY_CLIENT_SECRET
  SENTRY                = var.SENTRY

  # Bot Config
  COMMIT_SHA            = var.COMMIT_SHA
  BACKEND               = var.BACKEND
  BOT_PREFIX            = var.BOT_PREFIX
  BOT_HOME_CHANNEL      = var.BOT_HOME_CHANNEL
  BOT_ADMINS            = var.BOT_ADMINS
  BOT_EXTRA_BACKEND_DIR = var.BOT_EXTRA_BACKEND_DIR
  RIOT_TOKEN            = var.RIOT_TOKEN
  RIOT_REGION           = var.RIOT_REGION
  RIOT_REGION_V5        = var.RIOT_REGION_V5
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
