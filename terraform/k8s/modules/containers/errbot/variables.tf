# ACR configuration
variable "ACR_NAME" {
  type = string
}

# Bot Config

variable "IMAGE_TAG" {
  type = string
  default = "test"
}

# Bot Creds

variable "CHAT_SERVICE_TOKEN" {
  type      = string
  sensitive = true
}

variable "RIOT_TOKEN" {
  type      = string
  sensitive = true
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
