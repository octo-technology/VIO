resource "google_compute_global_address" "static" {
  name         = "tf-${var.project_name}-ip"
}