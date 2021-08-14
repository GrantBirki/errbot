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

  client_secret   = var.client_secret
  client_id       = var.client_id
  tenant_id       = var.tenant_id
  subscription_id = var.subscription_id
}

module "errbot_container" {
  source = "./modules/container"

  # Azure Creds
  client_secret   = var.client_secret
  client_id       = var.client_id
  tenant_id       = var.tenant_id
  subscription_id = var.subscription_id

  # Bot Creds
  CHAT_SERVICE_TOKEN = var.CHAT_SERVICE_TOKEN

  # Bot Config

  BACKEND               = var.BACKEND
  BOT_PREFIX            = var.BOT_PREFIX
  BOT_ADMINS            = var.BOT_ADMINS
  BOT_EXTRA_BACKEND_DIR = var.BOT_EXTRA_BACKEND_DIR
  RIOT_TOKEN            = var.RIOT_TOKEN
  RIOT_REGION           = var.RIOT_REGION
  SUMMONER_LIST         = var.SUMMONER_LIST

  # Project Variables
  azure_resource_group = "errbot"
  project_name         = "errbot"
  azure_location       = "centralus"

  commands = []

  # Container Resources
  cpu         = 1
  memory      = 1
  project_env = "prod"
  image_tag   = var.IMAGE_TAG
}
