resource "google_service_account" "service_account" {
  display_name = "tf-service-account"
  account_id   = "tf-service-account"
  project      = var.project_id
}

locals {
  all_service_account_roles = concat(var.service_account_roles, [
    "roles/iam.serviceAccountTokenCreator",
    "roles/container.serviceAgent",
    "roles/container.nodeServiceAccount",
#    "roles/artifactregistry.serviceAgent"
  ])
}

resource "google_project_iam_member" "service_account-roles" {
  for_each = toset(local.all_service_account_roles)

  project = var.project_id
  role    = each.value
  member  = "serviceAccount:${google_service_account.service_account.email}"
}

