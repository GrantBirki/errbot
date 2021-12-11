data "kubectl_file_documents" "nginx_namespace_manifest" {
  content = file("modules/containers/nginx/namespace.yaml")
}

resource "kubectl_manifest" "nginx_namespace" {
  count     = length(data.kubectl_file_documents.nginx_namespace_manifest.documents)
  yaml_body = element(data.kubectl_file_documents.nginx_namespace_manifest.documents, count.index)
}
