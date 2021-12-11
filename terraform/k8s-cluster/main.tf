# Configure the Microsoft Azure Provider
provider "azurerm" {
  features {}
  # Ignore Auth Warnings
  skip_provider_registration = true

  client_id       = var.CLIENT_ID
  client_secret   = var.CLIENT_SECRET
  tenant_id       = var.TENANT_ID
  subscription_id = var.SUBSCRIPTION_ID
}

# The Azure Subnet for the AKS cluster
resource "azurerm_virtual_network" "vnet" {
  name                = "${var.PROJECT_NAME}_${var.ENVIRONMENT}_containers"
  location            = var.CLOUD_LOCATION
  resource_group_name = azurerm_resource_group.default.name
  address_space       = ["10.2.0.0/16"]
  tags = {
    created_by = "terraform"
  }
}
resource "azurerm_subnet" "subnet" {
  address_prefixes     = ["10.2.0.0/24"]
  name                 = "${var.PROJECT_NAME}_${var.ENVIRONMENT}_default_subnet"
  resource_group_name  = azurerm_resource_group.default.name
  virtual_network_name = azurerm_virtual_network.vnet.name

  # delegation {

  #   name = "${var.PROJECT_NAME}_${var.ENVIRONMENT}_subnet_delegation"
  #   service_delegation {
  #     name    = "Microsoft.ContainerInstance/containerGroups"
  #     actions = ["Microsoft.Network/virtualNetworks/subnets/action"]
  #   }

  # }
}

resource "azurerm_resource_group" "default" {
  name     = "${var.PROJECT_NAME}-k8s-rg-${var.ENVIRONMENT}"
  location = var.CLOUD_LOCATION

  tags = {
    created_by = "Terraform"
  }
}

resource "azurerm_kubernetes_cluster" "default" {
  name                = "${var.PROJECT_NAME}-k8s-aks-${var.ENVIRONMENT}"
  location            = azurerm_resource_group.default.location
  resource_group_name = azurerm_resource_group.default.name
  dns_prefix          = "${var.PROJECT_NAME}-k8s-${var.ENVIRONMENT}"
  sku_tier            = "Free"

  network_profile {
    network_plugin = "azure"
    network_policy = "calico"
  }

  default_node_pool {
    name            = "default"
    node_count      = var.NODE_COUNT
    vm_size         = var.VM_SIZE
    os_disk_size_gb = var.NODE_DISK_SIZE_GB
    vnet_subnet_id  = azurerm_subnet.subnet.id
  }

  service_principal {
    client_id     = var.CLIENT_ID
    client_secret = var.CLIENT_SECRET
  }

  role_based_access_control {
    enabled = true
  }

  tags = {
    created_by = "Terraform"
  }
}

# Attach the K8s cluster to ACR

data "azuread_service_principal" "aks_principal" {
  application_id = var.CLIENT_ID
}

resource "azurerm_role_assignment" "acrpull_role" {
  scope                            = azurerm_container_registry.acr.id
  role_definition_name             = "AcrPull"
  principal_id                     = data.azuread_service_principal.aks_principal.id
  skip_service_principal_aad_check = true
}
