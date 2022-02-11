data "kubectl_path_documents" "promtail_configmap_manifest" {
  vars = {
    LOKI_PUSH_URL            = "${var.LOKI_PUSH_URL}"
  }
  pattern = "modules/daemonsets/promtail/promtail-config.yaml"
}

resource "kubectl_manifest" "promtail_configmap" {
  count     = length(data.kubectl_path_documents.promtail_configmap_manifest.documents)
  yaml_body = element(data.kubectl_path_documents.promtail_configmap_manifest.documents, count.index)
}
