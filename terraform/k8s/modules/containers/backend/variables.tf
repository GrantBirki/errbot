variable "IMAGE_TAG" {
  description = "The image tag to use for deployments"
  default     = "latest"
  type        = string
}

variable "ENVIRONMENT" {
  description = "The Environment which all containers are running in (dev/prod)"
  type        = string
  default     = "prod"
}

variable "ENVIRONMENT_CONTEXT" {
  description = "The Environment context which all containers are running in (kube)"
  type        = string
  default     = "kube"
}

variable "ACR_NAME" {
  description = "The name of the Azure Container Registry"
  type = string
}
