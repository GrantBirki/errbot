terraform {
  backend "remote" {
    organization = "errbot"

    workspaces {
      name = "errbot-containers"
    }
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
  CHAT_SERVICE_TOKEN = var.CHAT_SERVICE_TOKEN

  # Bot Config
  BACKEND               = var.BACKEND
  BOT_PREFIX            = var.BOT_PREFIX
  BOT_ADMINS            = var.BOT_ADMINS
  BOT_EXTRA_BACKEND_DIR = var.BOT_EXTRA_BACKEND_DIR
  RIOT_TOKEN            = var.RIOT_TOKEN
  RIOT_REGION           = var.RIOT_REGION

  # Project Variables
  azure_resource_group = "errbot"
  project_name         = "errbot"
  azure_location       = "West US 2"

  commands = []

  # Container Resources
  cpu         = 1
  memory      = 1
  project_env = "prod"
  image_tag   = var.IMAGE_TAG
}
