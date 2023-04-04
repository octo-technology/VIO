resource "google_compute_address" "static" {
  name = "tf-${var.project_name}-ip"
  region = var.region
}