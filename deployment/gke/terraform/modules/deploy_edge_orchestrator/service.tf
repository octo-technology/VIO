resource "kubernetes_service" "airbus_vio_orchestrator" {
  metadata {
    name      = "${var.name}"
    namespace = var.namespace

    labels = {
      app = var.name
      "app.kubernetes.io/component" = "back"
      "app.kubernetes.io/instance"  = var.namespace
      "app.kubernetes.io/name"      = var.name
    }

    annotations = {
      "cloud.google.com/neg" = "{\"ingress\":true}"
    }
  }

  spec {
    port {
      name        = "http"
      port        = 8000
      target_port = "8000"
    }

    selector = {
      "app.kubernetes.io/component" = "back"
      "app.kubernetes.io/instance"  = var.namespace
      "app.kubernetes.io/name"      = var.name
    }

    type                    = "LoadBalancer"
    session_affinity        = "None"
    external_traffic_policy = "Cluster"
    ip_families             = ["IPv4"]
  }
}

