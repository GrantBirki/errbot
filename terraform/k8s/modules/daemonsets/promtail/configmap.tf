data "kubectl_path_documents" "promtail_configmap_manifest" {
  sensitive_vars = {
    LOKI_PUSH_URL = "${var.LOKI_PUSH_URL}"
  }
  pattern = "modules/daemonsets/promtail/promtail-config.yaml"
}

resource "kubectl_manifest" "promtail_configmap" {
  count     = length(data.kubectl_path_documents.promtail_configmap_manifest.documents)
  yaml_body = element(data.kubectl_path_documents.promtail_configmap_manifest.documents, count.index)

  # hide all the output from the yaml_body as it contains sensitive data
  # ref: https://registry.terraform.io/providers/gavinbunney/kubectl/latest/docs/resources/kubectl_manifest#sensitive-fields
  sensitive_fields = ["data"]
}
