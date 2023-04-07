resource "kubernetes_deployment" "airbus_vio_orchestrator" {
  metadata {
    name      = var.name
    namespace = var.namespace

    labels = {
      app = var.name
    }
  }

  spec {
    replicas = 2
    selector {
      match_labels = {
        "app.kubernetes.io/component" = "back"
        "app.kubernetes.io/instance" = var.namespace
        "app.kubernetes.io/name" = var.namespace
      }
    }

    template {
      metadata {
        labels = {
          "app.kubernetes.io/component" = "back"
          "app.kubernetes.io/instance" = var.namespace
          "app.kubernetes.io/name" = var.namespace
        }
      }

      spec {
        volume {
          name = "service-account-credentials-volume"
          secret {
            secret_name = "service-account-credentials"
            items {
              key  = "sa_json"
              path = "sa_credentials.json"
            }
          }
        }
        container {
          name  = var.name
          image = "europe-west1-docker.pkg.dev/acn-gcp-octo-sas/tf-airbus-vio-artifacts/edge_orchestrator:0.5.1"

          port {
            name           = "http"
            container_port = 8000
            protocol       = "TCP"
          }

          env {
            name  = "API_CONFIG"
            value = "upload-gcp"
          }
          env {
            name  = "GOOGLE_APPLICATION_CREDENTIALS"
            value = "/etc/gcp/sa_credentials.json"
          }
          env {
            name  = "GCP_BUCKET_NAME"
            value = "airbus-vio-storage"
          }

          volume_mount {
            name       = "service-account-credentials-volume"
            read_only  = true
            mount_path = "/etc/gcp"
          }

          liveness_probe {
            http_get {
              path = "/"
              port = "http"
            }

            initial_delay_seconds = 30
            period_seconds        = 5
          }
          readiness_probe {
            http_get {
              path = "/"
              port = "http"
            }

            initial_delay_seconds = 30
            period_seconds        = 5
          }
          startup_probe {
            http_get {
              path = "/"
              port = "http"
            }

            initial_delay_seconds = 10
            period_seconds        = 5
            success_threshold     = 1
            failure_threshold     = 60
          }
          image_pull_policy = "IfNotPresent"
        }
        restart_policy = "Always"
      }
    }

    strategy {
      type = "RollingUpdate"
      rolling_update {
        max_unavailable = "25%"
        max_surge       = "25%"
      }
    }

    revision_history_limit    = 10
    progress_deadline_seconds = 600
  }
}

