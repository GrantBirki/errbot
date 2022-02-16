data "kubectl_path_documents" "errbot_namespace_manifest" {
  vars = {
    NAMESPACE = "${var.NAMESPACE}"
  }
  pattern = "modules/containers/errbot/namespace.yaml"
}

resource "kubectl_manifest" "errbot_namespace" {
  count     = length(data.kubectl_path_documents.errbot_namespace_manifest.documents)
  yaml_body = element(data.kubectl_path_documents.errbot_namespace_manifest.documents, count.index)
}
