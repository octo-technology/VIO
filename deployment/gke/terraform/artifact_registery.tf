resource "google_artifact_registry_repository" "tf_artifact_registery" {
  location      = var.region
  repository_id = "tf-${var.project_name}-artifacts"
  description   = "Docker repository for ${var.project_name}"
  format        = "DOCKER"
}