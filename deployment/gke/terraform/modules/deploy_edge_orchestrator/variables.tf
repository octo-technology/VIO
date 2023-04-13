variable "project_name" {
  type = string
  description = "project name"
}

variable "name" {
  type = string
  description = "app name"
}

variable "namespace" {
  type = string
  description = "namespace name"
}

variable "gcp_bucket_name" {
  type = string
  description = "gcp bucket name"
}

variable "secret_name" {
  type = string
  description = "service account name"
}

locals {
  secret_volume_name = "${var.secret_name}-volume"
}