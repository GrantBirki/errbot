module "errbot" {
  source = "./modules/containers/errbot"
  # Environment variables
  IMAGE_TAG = var.IMAGE_TAG
  # Bot Creds
  CHAT_SERVICE_TOKEN    = var.CHAT_SERVICE_TOKEN
  AWS_ACCESS_KEY_ID     = var.AWS_ACCESS_KEY_ID_ENCODED
  AWS_SECRET_ACCESS_KEY = var.AWS_SECRET_ACCESS_KEY_ENCODED
  RIOT_TOKEN            = var.RIOT_TOKEN
  SPOTIFY_CLIENT_ID     = var.SPOTIFY_CLIENT_ID
  SPOTIFY_CLIENT_SECRET = var.SPOTIFY_CLIENT_SECRET
  SENTRY                = var.SENTRY

  # Config
  ACR_NAME  = data.azurerm_container_registry.acr.name
  NAMESPACE = "errbot"
}

module "errbot_public" {
  source = "./modules/containers/errbot"
  # Environment variables
  IMAGE_TAG = var.IMAGE_TAG
  # Bot Creds
  CHAT_SERVICE_TOKEN    = var.CHAT_SERVICE_TOKEN_PUBLIC
  AWS_ACCESS_KEY_ID     = var.AWS_ACCESS_KEY_ID_ENCODED
  AWS_SECRET_ACCESS_KEY = var.AWS_SECRET_ACCESS_KEY_ENCODED
  RIOT_TOKEN            = var.RIOT_TOKEN
  SPOTIFY_CLIENT_ID     = var.SPOTIFY_CLIENT_ID
  SPOTIFY_CLIENT_SECRET = var.SPOTIFY_CLIENT_SECRET
  SENTRY                = var.SENTRY

  # Config
  ACR_NAME  = data.azurerm_container_registry.acr.name
  NAMESPACE = "errbot-public"
}

module "promtail" {
  source = "./modules/daemonsets/promtail"
  # Secrets
  LOKI_PUSH_URL = var.LOKI_PUSH_URL
}
