terraform {

  required_version = "=1.0.4"

  # Using the Azure Provider
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "=2.46.0"
    }
  }
}

data "azurerm_container_registry" "acr" {
  name                = var.project_name
  resource_group_name = var.azure_resource_group

  depends_on = [
    azurerm_container_registry.acr
  ]
}

resource "azurerm_container_registry" "acr" {
  name                = var.project_name
  resource_group_name = var.azure_resource_group
  location            = var.azure_location
  sku                 = "Basic"
  admin_enabled       = true
  # georeplication_locations = ["Central US"]
  # retention_policy {
  #   enabled = true
  # }

  tags = {
    managed_by = "terraform"
  }

}

resource "azurerm_virtual_network" "vnet" {
  name                = "${var.project_name}_${var.project_env}_containers"
  location            = var.azure_location
  resource_group_name = var.azure_resource_group
  address_space       = ["10.2.0.0/16"]
  tags = {
    managed_by = "terraform"
  }
}

resource "azurerm_subnet" "subnet" {
  address_prefixes     = ["10.2.0.0/24"]
  name                 = "${var.project_name}_${var.project_env}_default_subnet"
  resource_group_name  = var.azure_resource_group
  virtual_network_name = azurerm_virtual_network.vnet.name

  delegation {

    name = "${var.project_name}_${var.project_env}_subnet_delegation"
    service_delegation {
      name    = "Microsoft.ContainerInstance/containerGroups"
      actions = ["Microsoft.Network/virtualNetworks/subnets/action"]
    }

  }
}

resource "azurerm_network_profile" "net_profile" {
  name                = "${var.project_name}_${var.project_env}_container_net_profile"
  location            = var.azure_location
  resource_group_name = var.azure_resource_group

  container_network_interface {
    name = "${var.project_name}_${var.project_env}_container_net_interface"

    ip_configuration {
      name      = "${var.project_name}_${var.project_env}_container_net_profile"
      subnet_id = azurerm_subnet.subnet.id
    }
  }
  tags = {
    managed_by = "terraform"
  }
}

resource "azurerm_container_group" "container_group" {
  ip_address_type     = "Private"
  network_profile_id  = azurerm_network_profile.net_profile.id
  location            = var.azure_location
  name                = "${var.project_name}-${var.project_env}"
  os_type             = "Linux"
  resource_group_name = var.azure_resource_group
  restart_policy      = "Always"
  tags = {
    managed_by = "terraform"
  }

  container {
    commands = var.commands
    cpu      = var.cpu
    environment_variables = {
      "ENV"                   = var.project_env
      "COMMIT_SHA"            = var.COMMIT_SHA
      "RIOT_REGION"           = var.RIOT_REGION
      "RIOT_REGION_V5"        = var.RIOT_REGION_V5
      "BOT_EXTRA_BACKEND_DIR" = var.BOT_EXTRA_BACKEND_DIR
      "BOT_PREFIX"            = var.BOT_PREFIX
      "BOT_HOME_CHANNEL"      = var.BOT_HOME_CHANNEL
      "BACKEND"               = var.BACKEND
      "COSMOS_ACCOUNT_HOST"   = var.COSMOS_ACCOUNT_HOST
      "COSMOS_DATABASE"       = var.COSMOS_DATABASE
      "COSMOS_CONTAINER"      = var.COSMOS_CONTAINER
      "DISABLE_LEAGUE_CRON"   = "true"
    }
    # image  = "${var.project_name}.azurecr.io/${var.project_name}:${var.project_env}-${var.image_tag}"
    image  = "${var.project_name}.azurecr.io/${var.project_name}:${var.image_tag}"
    memory = var.memory
    name   = "${var.project_name}-${var.project_env}"
    secure_environment_variables = {
      "CHAT_SERVICE_TOKEN"    = var.CHAT_SERVICE_TOKEN
      "BOT_ADMINS"            = var.BOT_ADMINS
      "RIOT_TOKEN"            = var.RIOT_TOKEN
      "COSMOS_ACCOUNT_KEY"    = var.COSMOS_ACCOUNT_KEY
      "AWS_ACCESS_KEY_ID"     = var.AWS_ACCESS_KEY_ID
      "AWS_SECRET_ACCESS_KEY" = var.AWS_SECRET_ACCESS_KEY
      "SPOTIFY_CLIENT_ID"     = var.SPOTIFY_CLIENT_ID
      "SPOTIFY_CLIENT_SECRET" = var.SPOTIFY_CLIENT_SECRET
      "SENTRY"                = var.SENTRY
    }

    ports {
      port     = 5000
      protocol = "TCP"
    }

  }

  image_registry_credential {
    server   = "${var.project_name}.azurecr.io"
    username = var.project_name
    password = data.azurerm_container_registry.acr.admin_password
  }

}
