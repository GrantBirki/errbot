data "kubectl_file_documents" "nginx_service_manifest" {
  depends_on = [
    data.kubectl_file_documents.nginx_namespace_manifest
  ]
  content = file("modules/containers/nginx/service.yaml")
}

resource "kubectl_manifest" "nginx_service" {
  depends_on = [
    data.kubectl_file_documents.nginx_namespace_manifest
  ]
  count     = length(data.kubectl_file_documents.nginx_service_manifest.documents)
  yaml_body = element(data.kubectl_file_documents.nginx_service_manifest.documents, count.index)
}
