# GKE cluster
resource "google_container_cluster" "main" {
  name     = local.cluster_name
  location = var.zone

  network    = var.vpc_name
  subnetwork = var.vpc_subnetwork
  networking_mode = "VPC_NATIVE"
  ip_allocation_policy {
    cluster_ipv4_cidr_block = "/21"
    services_ipv4_cidr_block = "/21"
  }

  # We can't create a cluster with no node pool defined, but we want to only use
  # separately managed node pools. So we create the smallest possible default
  # node pool and immediately delete it.
  remove_default_node_pool = true
  initial_node_count       = 1

  node_config {
    machine_type = "e2-medium"
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform",
    ]

    tags         = var.default_tags
    labels       = {
      env = var.project_id
    }

    metadata     = {
      disable-legacy-endpoints = "true"
    }
  }
}

# Separately Managed Node Pool
resource "google_container_node_pool" "main" {
  name       = "tf-node-pool-gke"
  location   = var.zone
  cluster    = google_container_cluster.main.name
  node_count = var.gke_num_nodes
  node_config {
    service_account = var.service_account_email
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform",
    ]

    machine_type = "e2-medium"

    tags         = var.default_tags
    labels       = {
      env = var.project_id
    }

    metadata     = {
      disable-legacy-endpoints = "true"
    }
  }

  depends_on = [
    google_container_cluster.main,
  ]
}

# Create GKE Namespace
resource "kubernetes_namespace" "main" {
  metadata {
    annotations = {
      name = var.namespace
    }
    name = var.namespace
  }
  depends_on = [
    google_container_cluster.main,
  ]
}