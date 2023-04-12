resource "kubernetes_deployment" "airbus_vio_interface" {
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
        "app.kubernetes.io/component" = "front"
        "app.kubernetes.io/instance" = var.namespace
        "app.kubernetes.io/name" = var.name
      }
    }

    template {
      metadata {
        labels = {
          "app.kubernetes.io/component" = "front"
          "app.kubernetes.io/instance" = var.namespace
          "app.kubernetes.io/name" = var.name
        }
      }

      spec {
        container {
          name  = var.name
          image = "europe-west1-docker.pkg.dev/acn-gcp-octo-sas/tf-airbus-vio-artifacts/edge_interface:0.5.1"

          port {
            name           = "http"
            container_port = 80
            protocol       = "TCP"
          }
#          liveness_probe {
#            http_get {
#              path = "/"
#              port = "http"
#            }
#            initial_delay_seconds = 30
#            period_seconds        = 5
#          }
#          readiness_probe {
#            http_get {
#              path = "/"
#              port = "http"
#            }
#            initial_delay_seconds = 30
#            period_seconds        = 5
#          }
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

