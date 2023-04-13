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

variable "gke_num_nodes" {
  default     = 1
  description = "number of gke nodes"
}

variable "default_tags" {
  default     = []
  description = "default tags"
}

variable "domain" {
  type = string
  description = "domain name"
}

variable "namespace" {
  type = string
  description = "namespace name"
}

variable "gcp_bucket_name" {
  type = string
  description = "gcp bucket name"
}

variable "tf_state_bucket_name" {
  type = string
  description = "bucket name for prod tf state"
}

locals {
  static_ip_name = "tf-${var.project_name}-ip"
  managed_certificate_name = "tf-${var.project_name}-cert"
}

variable "secret_name" {
  type = string
  description = "service account name"
}
