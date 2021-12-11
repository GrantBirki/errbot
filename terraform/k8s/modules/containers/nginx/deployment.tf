data "kubectl_path_documents" "nginx_deployment_manifest" {
  depends_on = [
    data.kubectl_file_documents.nginx_namespace_manifest
  ]

  vars = {
    IMAGE_TAG = "${var.IMAGE_TAG}"
    ACR_NAME  = "${var.ACR_NAME}"
  }
  pattern = "modules/containers/nginx/deployment.yaml"
}

resource "kubectl_manifest" "nginx_deployment" {
  depends_on = [
    data.kubectl_file_documents.nginx_namespace_manifest
  ]
  count     = length(data.kubectl_path_documents.nginx_deployment_manifest.documents)
  yaml_body = element(data.kubectl_path_documents.nginx_deployment_manifest.documents, count.index)
}
