project_id           = "acn-gcp-octo-sas"
project_name         = "airbus-vio"
region               = "europe-west1"
zone                 = "europe-west1-b"

custom_vpc           = false
vpc_name             = "sas-network"
vpc_subnetwork       = "europe-west1-sn"
default_tags         = ["allow-http", "allow-https", "ssh-from-home-whitelist", "ssh-from-innovate"]
gke_num_nodes        = 2
domain               = "vio.octo.tools"

app_name             = "edge-interface"
api_name             = "edge-orchestrator"

namespace            = "airbus-vio"
gcp_bucket_name      = "tf-airbus-vio-bucket"
secret_name          = "service-account-credentials"

tf_state_bucket_name = "tf-state-prod"
service_account_name = "tf-service-account"