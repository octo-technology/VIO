# Copyright (c) HashiCorp, Inc.
# SPDX-License-Identifier: MPL-2.0

# GKE cluster
resource "google_container_cluster" "primary" {
  name     = "tf-${var.project_name}-gke"
  location = var.zone

  # We can't create a cluster with no node pool defined, but we want to only use
  # separately managed node pools. So we create the smallest possible default
  # node pool and immediately delete it.
  remove_default_node_pool = true
  initial_node_count       = 1

  network    = var.vpc_name
  subnetwork = var.vpc_subnetwork

  node_config {
    machine_type = "e2-small"
    oauth_scopes    = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
    tags = var.default_tags
  }
}

# Separately Managed Node Pool
resource "google_container_node_pool" "primary_nodes" {
  name       = "tf-node-pool-gke"
  location   = var.zone
  cluster    = google_container_cluster.primary.name
  node_count = var.gke_num_nodes
  node_config {
    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform",
    ]

    labels = {
      env = var.project_id
    }

    machine_type = "e2-medium"
    tags         = var.default_tags
    metadata = {
      disable-legacy-endpoints = "true"
    }
  }
}
