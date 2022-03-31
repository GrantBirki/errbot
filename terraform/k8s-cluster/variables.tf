# You may edit any of the default values in this file to tweak your cluster settings
# Examples: Change the number of nodes, the size of your nodes, your nodes storage, the name of your cluster, the region, etc

variable "PROJECT_NAME" {
  description = "The name of your project"
  default     = "errbot" # Change the name here to something unique for your own cluster (CHANGE ME)
  type        = string
}

variable "ENVIRONMENT" {
  description = "The Environment context which all containers are running in (dev/prod)"
  type        = string
  default     = "prod"
}

variable "NODE_COUNT" {
  description = "Number of Nodes in your K8s cluster"
  default     = 1
  type        = number
}

variable "VM_SIZE" {
  description = "Size of the VM to create"
  default     = "Standard_B2s"
  type        = string
}

variable "CLOUD_LOCATION" {
  description = "Location/Region for the cloud provider to deploy your cluster in"
  default     = "West US 2"
  type        = string
}

variable "NODE_DISK_SIZE_GB" {
  description = "The size in GB of the storage on each node"
  # This needs to be 30GB minimum or Azure API will say "no no no"
  default = 30
  type    = number
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
