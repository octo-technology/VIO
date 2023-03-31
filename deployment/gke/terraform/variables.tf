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

variable "gke_username" {
  default     = ""
  description = "gke username"
}

variable "gke_password" {
  default     = ""
  description = "gke password"
}

variable "gke_num_nodes" {
  default     = 1
  description = "number of gke nodes"
}