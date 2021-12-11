data "kubectl_file_documents" "errbot_namespace_manifest" {
  content = file("modules/containers/errbot/namespace.yaml")
}

resource "kubectl_manifest" "errbot_namespace" {
  count     = length(data.kubectl_file_documents.errbot_namespace_manifest.documents)
  yaml_body = element(data.kubectl_file_documents.errbot_namespace_manifest.documents, count.index)
}
