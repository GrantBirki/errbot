module "cert_manager" {
  source = "./modules/cert-manager"
}

module "kong" {
  source = "./modules/kong"
}

module "monitoring" {
  source = "./modules/monitoring"
}

module "frontend" {
  source = "./modules/containers/frontend"
  # Environment variables
  IMAGE_TAG   = var.FRONTEND_IMAGE_TAG
  ENVIRONMENT = var.ENVIRONMENT

  # Config
  ACR_NAME = data.azurerm_container_registry.acr.name
}

module "backend" {
  source = "./modules/containers/backend"
  # Environment variables
  IMAGE_TAG   = var.BACKEND_IMAGE_TAG
  ENVIRONMENT = var.ENVIRONMENT

  # Config
  ACR_NAME = data.azurerm_container_registry.acr.name
}
