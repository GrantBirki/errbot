# Namespace
variable "NAMESPACE" {
  description = "The namespace to deploy bot resources into"
  default     = "errbot"
  type        = string
}

# Container configuration
variable "REQUESTS_CPU" {
  description = "The CPU units to request on container creation"
  default     = "0.5"
  type        = string
}

variable "REQUESTS_MEMORY" {
  description = "The memory units to request on container creation"
  default     = "400Mi"
  type        = string
}

variable "LIMITS_CPU" {
  description = "The CPU units to limit the container to"
  default     = "1.4"
  type        = string
}

variable "LIMITS_MEMORY" {
  description = "The memory units to limit the container to"
  default     = "3Gi"
  type        = string
}

# ACR configuration
variable "ACR_NAME" {
  type = string
}

# Bot Config

variable "IMAGE_TAG" {
  type    = string
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
