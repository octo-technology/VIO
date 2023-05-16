project_id           = "acn-gcp-octo-sas"
project_name         = "vio"
region               = "europe-west1"
zone                 = "europe-west1-b"

custom_vpc           = false
vpc_name             = "sas-network"
vpc_subnetwork       = "europe-west1-sn"
default_tags         = ["allow-http", "allow-https", "ssh-from-home-whitelist", "ssh-from-innovate"]
gke_num_nodes        = 2


namespace            = "vio"
gcp_bucket_name      = "tf-vio-bucket"

service_account_name = "tf-service-account"

