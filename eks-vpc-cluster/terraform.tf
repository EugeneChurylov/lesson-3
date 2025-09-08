terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  # Локальний бекенд — безпечно, без витрат
  backend "local" {
    path = "tfstate/root.tfstate"
  }
}