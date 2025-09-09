# Провайдери читають ~/.kube/config. Можна вказати конкретний context.
provider "kubernetes" {
  config_path    = pathexpand("~/.kube/config")
  config_context = var.kube_context # якщо null, візьме current-context
}

provider "helm" {
  kubernetes {
    config_path    = pathexpand("~/.kube/config")
    config_context = var.kube_context
  }
}

# Namespace для ArgoCD
resource "kubernetes_namespace" "argocd_ns" {
  metadata {
    name = var.namespace
    labels = {
      "app.kubernetes.io/part-of" = "argocd"
    }
  }
}

# Helm-реліз ArgoCD
resource "helm_release" "argocd" {
  name             = "argocd"
  repository       = "https://argoproj.github.io/argo-helm"
  chart            = "argo-cd"
  version          = var.argocd_version
  namespace        = kubernetes_namespace.argocd_ns.metadata[0].name
  create_namespace = false

  values = [
    file("${path.module}/values/argocd-values.yaml")
  ]

  # Очікуємо створення CRD і подів
  timeout = 600
  wait    = true
}

output "argocd_namespace" {
  value = kubernetes_namespace.argocd_ns.metadata[0].name
}

output "argocd_release_name" {
  value = helm_release.argocd.name
}
