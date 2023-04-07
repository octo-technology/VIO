resource "google_compute_managed_ssl_certificate" "default" {
  name        = local.managed_certificate_name
  description = "${var.project_name} default certificate"
  managed {
    domains = [
        "${var.domain}"
      ]
  }
}