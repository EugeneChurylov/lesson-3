variable "kube_context" {
  description = "Kubeconfig context to use (EKS cluster context name)"
  type        = string
  default     = null
}

variable "namespace" {
  description = "Namespace for ArgoCD"
  type        = string
  default     = "infra-tools"
}

variable "argocd_version" {
  description = "ArgoCD Helm chart version"
  type        = string
  default     = "5.51.6" # популярна стабільна версія чарту argo/argo-cd
}
