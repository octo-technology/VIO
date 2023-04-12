provider "google" {
  project = var.project_id
  region  = var.region
}

provider "kubernetes" {
  config_path = "~/.kube/config"
}

module "create_infra_ressources" {
  source          = "./modules/create_infra_ressources"

  project_id      = var.project_id
  project_name    = var.project_name
  region          = var.region
  zone            = var.zone

  custom_vpc      = var.custom_vpc
  vpc_name        = var.vpc_name
  vpc_subnetwork  = var.vpc_subnetwork
  default_tags    = var.default_tags

  namespace       = var.namespace
  gcp_bucket_name = var.gcp_bucket_name
}

module "edge_interface" {
  source         = "./modules/deploy_edge_interface"

  name           = "edge-interface"
  project_name   = var.project_name
  namespace      = var.namespace
}

module "edge_orchestrator" {
  source          = "./modules/deploy_edge_orchestrator"

  name            = "edge-orchestrator"
  project_name    = var.project_name
  namespace       = var.namespace
  gcp_bucket_name = var.gcp_bucket_name
}
