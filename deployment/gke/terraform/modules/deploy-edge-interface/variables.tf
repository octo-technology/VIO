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

locals {
  static_ip_name = "tf-${var.project_name}-ip"
  managed_certificate_name = "tf-${var.project_name}-cert"
}