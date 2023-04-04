resource "google_storage_bucket" "basic" {
  name     = "tf-${var.project_name}-bucket"
  location = var.region
  force_destroy = true
}