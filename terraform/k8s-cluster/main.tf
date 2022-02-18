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

# The security group to assign to the subnet below
resource "azurerm_network_security_group" "nsg" {
  name                = "${var.PROJECT_NAME}_nsg"
  location            = var.CLOUD_LOCATION
  resource_group_name = azurerm_resource_group.default.name

  security_rule {
    name                       = "block-aks-inbound"
    priority                   = 100
    direction                  = "Inbound"
    access                     = "Deny"
    protocol                   = "*"
    source_port_range          = "*"
    destination_port_range     = "*"
    source_address_prefix      = "*"
    destination_address_prefix = "*"
  }

  tags = {
    created_by = "terraform"
  }
}

# The Azure Subnet for the AKS cluster
resource "azurerm_virtual_network" "vnet" {
  name                = "${var.PROJECT_NAME}_vnet"
  location            = var.CLOUD_LOCATION
  resource_group_name = azurerm_resource_group.default.name
  address_space       = ["10.2.0.0/16"]
  tags = {
    created_by = "terraform"
  }
}

# Create the subnet inside the vnet
resource "azurerm_subnet" "subnet" {
  address_prefixes     = ["10.2.0.0/24"]
  name                 = "${var.PROJECT_NAME}_default_subnet"
  resource_group_name  = azurerm_resource_group.default.name
  virtual_network_name = azurerm_virtual_network.vnet.name
}

# Link the subnet to the security group
resource "azurerm_subnet_network_security_group_association" "nsg_association" {
  subnet_id                 = azurerm_subnet.subnet.id
  network_security_group_id = azurerm_network_security_group.nsg.id
}

resource "azurerm_resource_group" "default" {
  name     = var.PROJECT_NAME
  location = var.CLOUD_LOCATION

  tags = {
    created_by = "Terraform"
  }
}

resource "azurerm_kubernetes_cluster" "aks" {
  name                = "${var.PROJECT_NAME}-k8s"
  location            = azurerm_resource_group.default.location
  resource_group_name = azurerm_resource_group.default.name
  dns_prefix          = "${var.PROJECT_NAME}-k8s"
  sku_tier            = "Free"

  role_based_access_control {
    enabled = true
  }

  network_profile {
    network_plugin    = "azure"
    network_policy    = "calico"
    load_balancer_sku = "basic"
  }

  default_node_pool {
    name            = "default"
    node_count      = var.NODE_COUNT
    vm_size         = var.VM_SIZE
    os_disk_size_gb = var.NODE_DISK_SIZE_GB
    vnet_subnet_id  = azurerm_subnet.subnet.id
  }

  identity {
    type = "SystemAssigned"
  }

  tags = {
    created_by = "Terraform"
  }
}
