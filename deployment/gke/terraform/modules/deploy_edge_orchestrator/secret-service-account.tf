resource "kubernetes_secret" "airbus_vio_orchestrator" {
  metadata {
    name      = var.secret_name
    namespace = var.namespace
  }

  type = "Opaque"

  data = {
    "sa_json" = jsonencode({
      "type": "service_account",
      "project_id": removed,
      "private_key_id": removed,
      "private_key": "-----BEGIN PRIVATE KEY-----\nremoved\n-----END PRIVATE KEY-----\n",
      "client_email": "removed",
      "client_id": "removed",
      "auth_uri": "https://accounts.google.com/o/oauth2/auth",
      "token_uri": "https://oauth2.googleapis.com/token",
      "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
      "client_x509_cert_url": "removed"
    })
  }
}

