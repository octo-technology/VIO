data "google_compute_global_address" "static" {
  name = "tf-${var.project_name}-ip"
}

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
        name = "${var.name}-service"
        port {
          number = 80
        }
      }
    }
  }
}

