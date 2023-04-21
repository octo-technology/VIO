variable "project_name" {
  type = string
  description = "project name"
}

variable "cluster_name" {
  type = string
  description = "cluster name"
}

variable "ingress_name" {
  type = string
  description = "ingress name"
}

variable "app_name" {
  type = string
  description = "app name"
}

variable "api_name" {
  type = string
  description = "api name"
}

variable "namespace" {
  type = string
  description = "namespace name"
}

locals {
  static_ip_name = "tf-${var.project_name}-ip"
#  static_ip_name = "tempo"
  managed_certificate_name = "vio"
}