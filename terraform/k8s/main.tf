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
  IMAGE_TAG = var.ERRBOT_IMAGE_TAG
  # Bot Creds
  CHAT_SERVICE_TOKEN    = var.CHAT_SERVICE_TOKEN
  AWS_ACCESS_KEY_ID     = var.AWS_ACCESS_KEY_ID
  AWS_SECRET_ACCESS_KEY = var.AWS_SECRET_ACCESS_KEY
  RIOT_TOKEN            = var.RIOT_TOKEN
  SPOTIFY_CLIENT_ID     = var.SPOTIFY_CLIENT_ID
  SPOTIFY_CLIENT_SECRET = var.SPOTIFY_CLIENT_SECRET
  SENTRY                = var.SENTRY

  # Config
  ACR_NAME = data.azurerm_container_registry.acr.name
}
