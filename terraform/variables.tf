# Azure Creds

variable "CLIENT_SECRET" {
  type = string
}

variable "CLIENT_ID" {
  type = string
}

variable "TENANT_ID" {
  type = string
}

variable "SUBSCRIPTION_ID" {
  type = string
}

# End Azure Creds

variable "IMAGE_TAG" {
  type    = string
  default = "test"
}

# Bot Creds

variable "CHAT_SERVICE_TOKEN" {
  type = string
}

# Bot config

variable "BACKEND" {
  type = string
}

variable "BOT_PREFIX" {
  type = string
}

variable "BOT_ADMINS" {
  type = string
}

variable "BOT_EXTRA_BACKEND_DIR" {
  type = string
}

variable "RIOT_TOKEN" {
  type = string
}

variable "RIOT_REGION" {
  type = string
}
