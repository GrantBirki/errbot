data "kubectl_path_documents" "status_page_network_policy_manifest" {
  depends_on = [
    data.kubectl_file_documents.status_page_namespace_manifest
  ]

  pattern = "modules/containers/status_page/network.yaml"
}

resource "kubectl_manifest" "status_page_network_policy" {
  depends_on = [
    data.kubectl_file_documents.status_page_namespace_manifest
  ]
  count     = length(data.kubectl_path_documents.status_page_network_policy_manifest.documents)
  yaml_body = element(data.kubectl_path_documents.status_page_network_policy_manifest.documents, count.index)
}
