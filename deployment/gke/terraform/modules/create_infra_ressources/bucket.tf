resource "google_storage_bucket" "basic" {
  name     = var.gcp_bucket_name
  location = var.region
  force_destroy = true
}