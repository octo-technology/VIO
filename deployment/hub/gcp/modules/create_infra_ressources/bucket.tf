resource "google_storage_bucket" "main" {
  name     = var.gcp_bucket_name
  location = var.region
  force_destroy = true
}