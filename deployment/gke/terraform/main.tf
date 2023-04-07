provider "google" {
  project = var.project_id
  region  = var.region
}

provider "kubernetes" {
  config_path = "~/.kube/config"
}

module "edge_interface" {
  source = "./modules/deploy-edge-interface"
  name   = "edge-interface"
  namespace   = var.namespace
  project_name   = var.project_name
}
