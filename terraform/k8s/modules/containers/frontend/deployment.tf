data "kubectl_path_documents" "frontend_deployment_manifest" {
  depends_on = [
    data.kubectl_file_documents.frontend_namespace_manifest
  ]

  vars = {
    ENVIRONMENT         = "${var.ENVIRONMENT}"
    IMAGE_TAG           = "${var.IMAGE_TAG}"
    ACR_NAME            = "${var.ACR_NAME}"
    ENVIRONMENT_CONTEXT = "${var.ENVIRONMENT_CONTEXT}"
  }
  pattern = "modules/containers/frontend/deployment.yaml"
}

resource "kubectl_manifest" "frontend_deployment" {
  depends_on = [
    data.kubectl_file_documents.frontend_namespace_manifest
  ]
  count     = length(data.kubectl_path_documents.frontend_deployment_manifest.documents)
  yaml_body = element(data.kubectl_path_documents.frontend_deployment_manifest.documents, count.index)
}
