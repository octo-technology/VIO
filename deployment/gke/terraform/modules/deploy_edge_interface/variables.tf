variable "project_name" {
  type = string
  description = "project name"
}

variable "name" {
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