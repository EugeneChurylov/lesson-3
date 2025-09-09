output "argocd_server_service" {
  description = "ArgoCD server Service name"
  value       = "argocd-server"
}

output "argocd_login_hint" {
  description = "Default login: admin / initial password from argocd-initial-admin-secret"
  value       = "kubectl -n ${var.namespace} get secret argocd-initial-admin-secret -o jsonpath='{.data.password}' | base64 --decode; echo"
}
