resource "google_compute_global_address" "static_ip" {
  name = var.static_ip
}