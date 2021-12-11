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

variable "ENVIRONMENT" {
  description = "The Environment context which all containers are running in (dev/prod)"
  type        = string
  default     = "prod"
}

# Bot Config

variable "ERRBOT_IMAGE_TAG" {
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

variable "AWS_ACCESS_KEY_ID_ENCODED" {
  type      = string
  sensitive = true
}

variable "AWS_SECRET_ACCESS_KEY_ENCODED" {
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

# Status page

variable "STATUS_PAGE_IMAGE_TAG" {
  description = "The image tag to use for status_page deployments"
  type        = string
  default     = "test"
}
