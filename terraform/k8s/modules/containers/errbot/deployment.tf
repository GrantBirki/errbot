data "kubectl_path_documents" "errbot_deployment_manifest" {
  depends_on = [
    data.kubectl_file_documents.errbot_namespace_manifest,
    data.kubectl_path_documents.errbot_secret_manifest
  ]

  vars = {
    COMMIT_SHA            = "${var.COMMIT_SHA}"
    ACR_NAME              = "${var.ACR_NAME}"
  }
  pattern = "modules/containers/errbot/deployment.yaml"
}

resource "kubectl_manifest" "errbot_deployment" {
  depends_on = [
    data.kubectl_file_documents.errbot_namespace_manifest
  ]
  count     = length(data.kubectl_path_documents.errbot_deployment_manifest.documents)
  yaml_body = element(data.kubectl_path_documents.errbot_deployment_manifest.documents, count.index)
}
