data "kubectl_path_documents" "errbot_deployment_manifest" {
  depends_on = [
    data.kubectl_path_documents.errbot_namespace_manifest,
    data.kubectl_path_documents.errbot_secret_manifest
  ]

  vars = {
    NAMESPACE              = "${var.NAMESPACE}"
    SERVER_LOCK_ALLOW_LIST = "${var.SERVER_LOCK_ALLOW_LIST}"
    IMAGE_TAG              = "${var.IMAGE_TAG}"
    ACR_NAME               = "${var.ACR_NAME}"
    REQUESTS_CPU           = "${var.REQUESTS_CPU}"
    REQUESTS_MEMORY        = "${var.REQUESTS_MEMORY}"
    LIMITS_CPU             = "${var.LIMITS_CPU}"
    LIMITS_MEMORY          = "${var.LIMITS_MEMORY}"
  }
  pattern = "modules/containers/errbot/deployment.yaml"
}

resource "kubectl_manifest" "errbot_deployment" {
  depends_on = [
    data.kubectl_path_documents.errbot_namespace_manifest
  ]
  count     = length(data.kubectl_path_documents.errbot_deployment_manifest.documents)
  yaml_body = element(data.kubectl_path_documents.errbot_deployment_manifest.documents, count.index)
}
