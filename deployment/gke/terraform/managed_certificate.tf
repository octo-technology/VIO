resource "google_certificate_manager_certificate" "default" {
  name        = "tf-${var.project_name}-cert"
  description = "${var.project_name} default certificate"
  scope       = "EDGE_CACHE"
  managed {
    domains = [
        "${var.domain}"
      ]
  }
}