resource "kubernetes_ingress_v1" "airbus_vio_interface" {
  metadata {
    name      = "${var.ingress_name}"
    namespace = var.namespace

    annotations = {
      "ingress.kubernetes.io/ingress.allow-http" = "true"
      "kubernetes.io/ingress.global-static-ip-name" = local.static_ip_name
#      "networking.gke.io/managed-certificates" = local.managed_certificate_name
      "ingress.gcp.kubernetes.io/pre-shared-cert"   = local.managed_certificate_name
    }
  }

  spec {
    default_backend {
      service {
        name = "${var.app_name}-front"
        port {
          number = 80
        }
      }
    }
    rule {
      host = "vio.octo.tools"
      http {
        path {
          backend {
            service {
              name = "${var.app_name}-front"
              port {
                number = 80
              }
            }
          }

          path = "/*"
        }
        path {
          backend {
            service {
              name = "${var.api_name}-api"
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

