# Copyright (c) HashiCorp, Inc.
# SPDX-License-Identifier: MPL-2.0

output "region" {
  value       = var.region
  description = "GCloud Region"
}

output "project_id" {
  value       = var.project_id
  description = "GCloud Project ID"
}

output "artifact_registery_name" {
  value       = google_artifact_registry_repository.tf_artifact_registery.name
  description = "Artifact registery name"
}

output "static_ip" {
  value       = google_compute_address.static.address
  description = "Static ip"
}

#output "kubernetes_cluster_name" {
#  value       = google_container_cluster.primary.name
#  description = "GKE Cluster Name"
#}
#
#output "kubernetes_cluster_host" {
#  value       = google_container_cluster.primary.endpoint
#  description = "GKE Cluster Host"
#}
