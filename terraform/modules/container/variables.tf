# Azure Creds

variable "client_secret" {
  type = string
}

variable "client_id" {
  type = string
}

variable "tenant_id" {
  type = string
}

variable "subscription_id" {
  type = string
}

# End Azure Creds

variable "azure_resource_group" {
  type = string
}

variable "commands" {
  description = "commands to run the container with"
  type        = list(string)
}

variable "azure_location" {
  type = string
}

variable "project_name" {
  type = string
}

variable "project_env" {
  type = string
}

variable "image_tag" {
  type = string
}

variable "memory" {
  type = number
}

variable "cpu" {
  type = number
}

# Bot creds

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

variable "SUMMONER_LIST" {
  type = string
}
