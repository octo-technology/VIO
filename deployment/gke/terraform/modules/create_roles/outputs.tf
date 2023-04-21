# Copyright (c) HashiCorp, Inc.
# SPDX-License-Identifier: MPL-2.0

output "service_account_name" {
  value       = google_service_account.service_account.account_id
  description = "Service account name"
}
output "service_account_email" {
  value       = google_service_account.service_account.email
  description = "Service account email"
}
