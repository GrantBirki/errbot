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
  # STATUS_PUSH_ENDPOINT  = var.STATUS_PUSH_ENDPOINT

  # Config
  ACR_NAME = data.azurerm_container_registry.acr.name
}
