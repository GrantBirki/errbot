data "kubectl_path_documents" "promtail_deployment_manifest" {
  depends_on = [
    data.kubectl_path_documents.promtail_configmap_manifest
  ]
  pattern = "modules/daemonsets/promtail/deployment.yaml"
}

resource "kubectl_manifest" "promtail_deployment" {
  depends_on = [
    data.kubectl_path_documents.promtail_configmap_manifest
  ]
  count     = length(data.kubectl_path_documents.promtail_deployment_manifest.documents)
  yaml_body = element(data.kubectl_path_documents.promtail_deployment_manifest.documents, count.index)

  # hide all the output from the yaml_body as it contains sensitive data
  # ref: https://registry.terraform.io/providers/gavinbunney/kubectl/latest/docs/resources/kubectl_manifest#sensitive-fields
  sensitive_fields = "data" 
}
