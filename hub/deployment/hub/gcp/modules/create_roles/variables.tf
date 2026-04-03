variable "project_id" {
  type = string
  description = "project id"
}

variable "service_account_name" {
  type = string
  description = "service account name"
}

variable "service_account_roles" {
  type        = list(string)
  description = "List of dataset names for which the Service Account will be data viewer"
  default     = []
}

