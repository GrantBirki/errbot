data "kubectl_file_documents" "frontend_service_manifest" {
  depends_on = [
    data.kubectl_file_documents.frontend_namespace_manifest
  ]
  content = file("modules/containers/frontend/service.yaml")
}

resource "kubectl_manifest" "frontend_service" {
  depends_on = [
    data.kubectl_file_documents.frontend_namespace_manifest
  ]
  count     = length(data.kubectl_file_documents.frontend_service_manifest.documents)
  yaml_body = element(data.kubectl_file_documents.frontend_service_manifest.documents, count.index)
}
