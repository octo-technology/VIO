variable "project_id" {
  type = string
  description = "project id"
}

variable "project_name" {
  type = string
  description = "project name"
}

variable "region" {
  type = string
  description = "region"
}

variable "zone" {
  description = "zone"
}

variable "custom_vpc" {
  type = bool
  description = "need to set up custom vpc"
}

variable "vpc_name" {
  description = "default vpc name"
}

variable "vpc_subnetwork" {
  description = "default vpc subnetwork name"
}

variable "gke_node_pool_name" {
  type = string
  description = "GKE node pool name"
}

variable "gke_num_nodes" {
  description = "number of gke nodes"
}

variable "default_tags" {
  default     = []
  description = "default tags"
}

variable "user_email_role_binding" {
  type     = string
  description = "user email for role binding"
}

variable "namespace" {
  type = string
  description = "namespace name"
}

variable "gcp_bucket_name" {
  type = string
  description = "gcp bucket name"
}

variable "service_account_name" {
  type = string
  description = "Service account name"
}

variable "service_account_email" {
  type = string
  description = "Service account email"
}

variable "static_ip" {
  type = string
  description = "Static ip name"
}

locals {
  cluster_name = "tf-${var.project_name}-gke"
  repo_id = "tf-${var.project_name}-artifacts"
}
