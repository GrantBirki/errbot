data "kubectl_path_documents" "errbot_secret_manifest" {
  depends_on = [
    data.kubectl_path_documents.errbot_namespace_manifest
  ]

  vars = {
    NAMESPACE = "${var.NAMESPACE}"
  }

  sensitive_vars = {
    CHAT_SERVICE_TOKEN    = "${var.CHAT_SERVICE_TOKEN}"
    RIOT_TOKEN            = "${var.RIOT_TOKEN}"
    AWS_ACCESS_KEY_ID     = "${var.AWS_ACCESS_KEY_ID}"
    AWS_SECRET_ACCESS_KEY = "${var.AWS_SECRET_ACCESS_KEY}"
    SPOTIFY_CLIENT_ID     = "${var.SPOTIFY_CLIENT_ID}"
    SPOTIFY_CLIENT_SECRET = "${var.SPOTIFY_CLIENT_SECRET}"
    SENTRY                = "${var.SENTRY}"
    GEOLOCATION_KEY       = "${var.GEOLOCATION_KEY}"
    IMAGE_TAG             = "${var.IMAGE_TAG}"
    ACR_NAME              = "${var.ACR_NAME}"
  }
  pattern = "modules/containers/errbot/secret.yaml"
}

resource "kubectl_manifest" "errbot_secret" {
  depends_on = [
    data.kubectl_path_documents.errbot_namespace_manifest
  ]
  count     = length(data.kubectl_path_documents.errbot_secret_manifest.documents)
  yaml_body = element(data.kubectl_path_documents.errbot_secret_manifest.documents, count.index)
}
