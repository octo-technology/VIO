# Copyright (c) HashiCorp, Inc.
# SPDX-License-Identifier: MPL-2.0

# VPC
resource "google_compute_network" "vpc" {
  count = var.custom_vpc ? 1 : 0

  name                    = "${var.project_id}-vpc"
  auto_create_subnetworks = "false"
}

# Subnet
resource "google_compute_subnetwork" "subnet" {
  count = var.custom_vpc ? 1 : 0

  name          = "${var.project_id}-subnet"
  region        = var.region
  network       = google_compute_network.vpc[0].name
  ip_cidr_range = "10.10.0.0/24"
}
