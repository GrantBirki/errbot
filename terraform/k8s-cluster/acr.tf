resource "azurerm_role_assignment" "role_acrpull" {
  scope                            = azurerm_container_registry.acr.id
  role_definition_name             = "AcrPull"
  principal_id                     = azurerm_kubernetes_cluster.aks.kubelet_identity.0.object_id
  skip_service_principal_aad_check = true
}

resource "azurerm_container_registry" "acr" {
  name                = "${var.PROJECT_NAME}acr" # Did you get an error saying that your repo must be globally unique? Try adding some extra charcters here
  resource_group_name = azurerm_resource_group.default.name
  location            = var.CLOUD_LOCATION
  sku                 = "Basic"
  admin_enabled       = true

  tags = {
    managed_by = "terraform"
  }
}
