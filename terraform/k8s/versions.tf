terraform {
  backend "remote" {
    organization = "errbot" # Change this to your own organization (CHANGE ME)

    workspaces {
      name = "errbot-k8s-workloads" # Change this to your own workspace name (CHANGE ME)
    }
  }
  required_version = "=1.1.0" # Change this to a different version if you want

  required_providers {
    kubectl = {
      source  = "gavinbunney/kubectl"
      version = ">= 1.7.0"
    }
  }
}
