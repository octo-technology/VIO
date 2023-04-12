resource "kubernetes_ingress_v1" "airbus_vio_interface" {
  metadata {
    name      = "${var.name}-front"
    namespace = var.namespace

    annotations = {
      "ingress.kubernetes.io/ingress.allow-http" = "false"
      "kubernetes.io/ingress.global-static-ip-name" = local.static_ip_name
      "networking.gke.io/managed-certificates" = local.managed_certificate_name
    }
  }

  spec {
    default_backend {
      service {
        name = "${var.name}-front"
        port {
          number = 80
        }
      }
    }
    rule {
      http {
        path {
          backend {
            service {
              name = "${var.name}-api"
              port {
                number = 8000
              }
            }
          }

          path = "/api"
        }
      }
    }
  }
}

