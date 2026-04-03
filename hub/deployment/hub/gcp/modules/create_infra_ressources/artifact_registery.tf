resource "google_artifact_registry_repository" "main" {
  location      = var.region
  repository_id = local.repo_id
  description   = "Docker repository for ${var.project_name}"
  format        = "DOCKER"
}