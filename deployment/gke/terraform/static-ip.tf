variable "project_name" {
  type = string
  description = "project name"
}

variable "custom_vpc" {
  type = bool
  description = "need to set up custom vpc"
}

resource "google_compute_address" "static" {
  name = "tf-${var.project_name}-ip"
  region = var.region
}