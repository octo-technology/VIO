# Copyright (c) HashiCorp, Inc.
# SPDX-License-Identifier: MPL-2.0

project_id = "acn-gcp-octo-sas"
region  = "europe-west1"
zone = "europe-west1-b"

project_name = "airbus-vio"

custom_vpc = false
vpc_name = "sas-network"
vpc_subnetwork = "europe-west1-sn"

default_tags = ["allow-http", "allow-https", "ssh-from-home-whitelist", "ssh-from-innovate"]

domain = "vio.octo.tools"