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

#provider "google" {
#  alias        = "impersonated"
#  access_token = data.google_service_account_access_token.default.access_token
#}
#
#data "google_client_openid_userinfo" "me" {
#  provider = google.impersonated
#}
#
#output "target-email" {
#  value = data.google_client_openid_userinfo.me.email
#}
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
  source                = "./modules/create_infra_ressources"

  project_id            = var.project_id
  project_name          = var.project_name
  region                = var.region
  zone                  = var.zone

  custom_vpc            = var.custom_vpc
  vpc_name              = var.vpc_name
  vpc_subnetwork        = var.vpc_subnetwork
  default_tags          = var.default_tags

  namespace             = var.namespace
  gcp_bucket_name       = var.gcp_bucket_name

  service_account_name  = var.service_account_name
  service_account_email = module.create_roles.service_account_email

  depends_on = [
    module.create_roles
  ]
}


module "edge_orchestrator" {
  source          = "./modules/deploy_edge_orchestrator"

  name            = var.api_name
  project_name    = var.project_name
  namespace       = var.namespace
  gcp_bucket_name = module.create_infra_ressources.gcp_bucket_name
  secret_name     = var.secret_name
}

module "edge_interface" {
  source         = "./modules/deploy_edge_interface"

  ingress_name   = "airbus-vio"
  app_name       = var.app_name
  api_name       = var.api_name
  project_name   = var.project_name
  cluster_name   = module.create_infra_ressources.cluster_name
  namespace      = var.namespace

  depends_on = [
    module.edge_orchestrator
  ]
}
