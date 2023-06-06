terraform {
  backend "gcs" {
    bucket  = "tf-state-vio-prod"
    prefix  = "terraform/state"
  }

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "4.59.0"
    }
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = ">= 2.0.1"
    }
  }

  required_version = ">= 0.14"
}

