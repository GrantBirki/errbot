terraform {
  backend "remote" {
    organization = "errbot" # Change this to your own organization (CHANGE ME)

    workspaces {
      name = "errbot-k8s-cluster" # Change this to your own workspace name (CHANGE ME)
    }
  }

  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "2.66.0"
    }
  }

  required_version = "=1.1.0" # Change this to a different version if you want
}
