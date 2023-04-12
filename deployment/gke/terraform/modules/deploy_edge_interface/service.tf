resource "kubernetes_service" "airbus_vio_interface" {
  metadata {
    name      = "${var.name}-front"
    namespace = var.namespace

    labels = {
      app = var.name
      "app.kubernetes.io/component" = "front"
      "app.kubernetes.io/instance" = var.namespace
      "app.kubernetes.io/name" = var.name
    }

    annotations = {
      "cloud.google.com/neg" = "{\"ingress\":true}"
    }
  }

  spec {
    port {
      name        = "http"
      port        = 80
      target_port = "80"
    }

    selector = {
      "app.kubernetes.io/component" = "front"
      "app.kubernetes.io/instance" = var.namespace
      "app.kubernetes.io/name" = var.name
    }

    type                    = "LoadBalancer"
    session_affinity        = "None"
    external_traffic_policy = "Cluster"
    ip_families             = ["IPv4"]
  }
}

