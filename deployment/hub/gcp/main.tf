provider "google" {
  project = var.project_id
  region  = var.region
}

data "google_service_account_access_token" "default" {
  target_service_account = module.create_roles.service_account_email
  scopes                 = ["userinfo-email", "cloud-platform"]
  lifetime               = "3600s"

  depends_on = [
    module.create_roles
  ]
}

provider "kubernetes" {
  host                   = "https://${module.create_infra_ressources.endpoint}"
  token                  = data.google_service_account_access_token.default.access_token
  cluster_ca_certificate = base64decode(module.create_infra_ressources.ca_certificate
  )
}

module "create_roles" {
  source               = "./modules/create_roles"

  project_id           = var.project_id
  service_account_name = var.service_account_name
}

module "create_infra_ressources" {
  source                  = "./modules/create_infra_ressources"

  project_id              = var.project_id
  project_name            = var.project_name
  region                  = var.region
  zone                    = var.zone

  custom_vpc              = var.custom_vpc
  vpc_name                = var.vpc_name
  vpc_subnetwork          = var.vpc_subnetwork
  default_tags            = var.default_tags
  gke_node_pool_name      = var.gke_node_pool_name
  gke_num_nodes           = var.gke_num_nodes

  user_email_role_binding = var.user_email_role_binding

  namespace               = var.namespace
  gcp_bucket_name         = var.gcp_bucket_name

  service_account_name    = var.service_account_name
  service_account_email   = module.create_roles.service_account_email

  static_ip               = var.static_ip

  depends_on = [
    module.create_roles
  ]
}
