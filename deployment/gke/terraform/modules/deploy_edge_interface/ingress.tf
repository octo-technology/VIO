resource "kubernetes_ingress_v1" "vio_interface" {
  metadata {
    name      = "${var.ingress_name}"
    namespace = var.namespace

    annotations = {
      "ingress.kubernetes.io/ingress.allow-http"    = "false"
      "kubernetes.io/ingress.global-static-ip-name" = local.static_ip_name
      "ingress.gcp.kubernetes.io/pre-shared-cert"   = var.managed_certificate_name
    }
  }

  spec {
    default_backend {
      service {
        name = "${var.app_name}"
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
              name = "${var.app_name}"
              port {
                number = 80
              }
            }
          }

          path = "/*"
        }
#        path {
#          backend {
#            service {
#              name = "${var.api_name}"
#              port {
#                number = 8000
#              }
#            }
#          }
#
#          path = "/api"
#        }
      }
    }
  }
}

