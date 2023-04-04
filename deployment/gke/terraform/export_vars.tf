# Export Terraform variable values to an Ansible var_file
resource "local_file" "tf_ansible_vars_file_new" {
  content = <<-DOC
    # Ansible vars_file containing variable values from Terraform.
    # Generated by Terraform mgmt configuration.

    tf_environment: ${var.project_id}
    tf_artifact_registery_name: ${google_artifact_registry_repository.tf_artifact_registery.repository_id}
    tf_front_static_ip_name: ${google_compute_address.static.name}
    tf_front_static_ip: ${google_compute_address.static.address}
    tf_bucket_name: ${google_storage_bucket.basic.name}
    DOC
  filename = "./tf_ansible_vars_file.yml"
}