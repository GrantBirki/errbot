data "kubectl_path_documents" "promtail_deployment_manifest" {
  depends_on = [
    data.kubectl_file_documents.promtail_configmap_manifest
  ]
  pattern = "modules/daemonsets/promtail/deployment.yaml"
}

resource "kubectl_manifest" "promtail_deployment" {
  depends_on = [
    data.kubectl_file_documents.promtail_configmap_manifest
  ]
  count     = length(data.kubectl_path_documents.promtail_deployment_manifest.documents)
  yaml_body = element(data.kubectl_path_documents.promtail_deployment_manifest.documents, count.index)
}
