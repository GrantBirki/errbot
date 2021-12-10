module "cert_manager" {
  source = "./modules/cert-manager"
}

module "kong" {
  source = "./modules/kong"
}

module "monitoring" {
  source = "./modules/monitoring"
}

module "status_page" {
  source = "./modules/containers/status_page"

  # Config
  ACR_NAME = data.azurerm_container_registry.acr.name

  # Environment variables
  IMAGE_TAG = var.STATUS_PAGE_IMAGE_TAG
}

module "errbot" {
  source = "./modules/containers/errbot"
  # Environment variables
  IMAGE_TAG   = var.ERRBOT_IMAGE_TAG

  # Config
  ACR_NAME = data.azurerm_container_registry.acr.name
}
