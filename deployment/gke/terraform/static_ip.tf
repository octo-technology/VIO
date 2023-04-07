resource "google_compute_global_address" "static" {
  name         = local.static_ip_name
}