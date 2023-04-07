resource "kubernetes_service" "airbus_vio_orchestrator" {
  metadata {
    name      = "${var.name}-api"
    namespace = var.namespace

    labels = {
      app = var.name
      "app.kubernetes.io/component" = "back"
      "app.kubernetes.io/instance" = var.namespace
      "app.kubernetes.io/name" = var.namespace
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
    cluster_ip = "10.151.240.20"

    selector = {
      "app.kubernetes.io/component" = "back"
      "app.kubernetes.io/instance" = var.namespace
      "app.kubernetes.io/name" = var.namespace
    }

    type                    = "LoadBalancer"
    session_affinity        = "None"
    external_traffic_policy = "Cluster"
    ip_families             = ["IPv4"]
  }
}

