# Bot Config

variable "COMMIT_SHA" {
  type = string
}

# Azure Creds

variable "CLIENT_SECRET" {
  type      = string
  sensitive = true
}

variable "CLIENT_ID" {
  type      = string
  sensitive = true
}

variable "TENANT_ID" {
  type      = string
  sensitive = true
}

variable "SUBSCRIPTION_ID" {
  type      = string
  sensitive = true
}

# End Azure Creds

variable "IMAGE_TAG" {
  type    = string
  default = "latest"
}

# Bot Creds

variable "CHAT_SERVICE_TOKEN" {
  type      = string
  sensitive = true
}

# Bot config

variable "BACKEND" {
  type = string
}

variable "BOT_PREFIX" {
  type = string
}

variable "BOT_HOME_CHANNEL" {
  type = string
}

variable "BOT_ADMINS" {
  type = string
}

variable "BOT_EXTRA_BACKEND_DIR" {
  type = string
}

variable "RIOT_TOKEN" {
  type      = string
  sensitive = true
}

variable "RIOT_REGION" {
  type = string
}

variable "RIOT_REGION_V5" {
  type = string
}

# AWS DynamoDB
variable "AWS_ACCESS_KEY_ID" {
  type      = string
  sensitive = true
}

variable "AWS_SECRET_ACCESS_KEY" {
  type      = string
  sensitive = true
}

# Spotify
variable "SPOTIFY_CLIENT_ID" {
  type      = string
  sensitive = true
}

variable "SPOTIFY_CLIENT_SECRET" {
  type      = string
  sensitive = true
}

# Sentry.io
variable "SENTRY" {
  type      = string
  sensitive = true
}
