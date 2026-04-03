resource "kubernetes_cluster_role" "main" {
  metadata {
    name = "cluster-admin"
  }

  rule {
    api_groups = [""]
    resources  = ["*"]
    verbs      = ["get", "list", "patch", "update", "watch"]
  }
}

resource "kubernetes_cluster_role_binding" "main" {
  metadata {
    name = "cluster-role-binding"
  }
  role_ref {
    api_group = "rbac.authorization.k8s.io"
    kind      = "ClusterRole"
    name      = "cluster-admin"
  }
  subject {
    kind      = "User"
    name      = var.user_email_role_binding
    api_group = "rbac.authorization.k8s.io"
  }
  subject {
    kind      = "ServiceAccount"
    name      = var.service_account_name
    namespace = var.namespace
  }
}