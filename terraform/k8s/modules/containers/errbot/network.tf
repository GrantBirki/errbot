data "kubectl_path_documents" "errbot_network_policy_manifest" {
  depends_on = [
    data.kubectl_path_documents.errbot_namespace_manifest
  ]

  vars = {
    NAMESPACE = "${var.NAMESPACE}"
  }

  pattern = "modules/containers/errbot/network.yaml"
}

resource "kubectl_manifest" "errbot_network_policy" {
  depends_on = [
    data.kubectl_path_documents.errbot_namespace_manifest
  ]
  count     = length(data.kubectl_path_documents.errbot_network_policy_manifest.documents)
  yaml_body = element(data.kubectl_path_documents.errbot_network_policy_manifest.documents, count.index)
}
