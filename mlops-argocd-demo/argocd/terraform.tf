terraform {
  required_version = ">= 1.5.0"
  required_providers {
    helm       = { source = "hashicorp/helm", version = "~> 2.11" }
    kubernetes = { source = "hashicorp/kubernetes", version = "~> 2.29" }
  }
  backend "local" {
    path = "tfstate/argocd.tfstate"
  }
}
