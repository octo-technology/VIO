output "cluster_name" {
  value       = google_container_cluster.main.name
  description = "Cluster name"
}

output "endpoint" {
  value       = google_container_cluster.main.endpoint
  description = "Cluster endpoint"
}

output "ca_certificate" {
  value       = google_container_cluster.main.master_auth[0].cluster_ca_certificate
  description = "Cluster certificate"
}

output "custom_namespace" {
  value       = kubernetes_namespace.main.metadata[0].name
  description = "Cluster namespace name"
}

output "gcp_bucket_name" {
  value       = google_storage_bucket.main.name
  description = "Bucket name"
}
