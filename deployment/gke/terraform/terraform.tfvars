# Copyright (c) HashiCorp, Inc.
# SPDX-License-Identifier: MPL-2.0

project_id           = "acn-gcp-octo-sas"
project_name         = "airbus-vio"
region               = "europe-west1"
zone                 = "europe-west1-b"

custom_vpc           = false
vpc_name             = "sas-network"
vpc_subnetwork       = "europe-west1-sn"
default_tags         = ["allow-http", "allow-https", "ssh-from-home-whitelist", "ssh-from-innovate"]

domain               = "vio.octo.tools"

namespace            = "airbus-vio"
gcp_bucket_name      = "tf-airbus-vio-bucket"
tf_state_bucket_name = "tf-state-prod"