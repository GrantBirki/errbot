# Bot Config

variable "COMMIT_SHA" {
  type = string
}

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
  default = "latest"
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

# Azure Cosmos DB
variable "COSMOS_ACCOUNT_HOST" {
  type = string
  default = "https://errbot-nosql-db.documents.azure.com:443/"
}

variable "COSMOS_DATABASE" {
  type = string
  default = "errbot"
}

variable "COSMOS_CONTAINER" {
  type = string
  default = "discord"
}

variable "COSMOS_ACCOUNT_KEY" {
  type = string
}

# AWS DynamoDB
variable "AWS_ACCESS_KEY_ID" {
  type = string
}

variable "AWS_SECRET_ACCESS_KEY" {
  type = string
}