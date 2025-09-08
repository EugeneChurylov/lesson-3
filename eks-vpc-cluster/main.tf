provider "aws" {
  region  = var.region
  profile = var.profile
}

locals {
  azs             = ["eu-central-1a", "eu-central-1b"]
  vpc_cidr        = "10.0.0.0/16"
  public_subnets  = ["10.0.1.0/24", "10.0.2.0/24"]
  private_subnets = ["10.0.101.0/24", "10.0.102.0/24"]
}

module "vpc" {
  source          = "./vpc"
  project         = var.project
  cidr            = local.vpc_cidr
  azs             = local.azs
  public_subnets  = local.public_subnets
  private_subnets = local.private_subnets
}

module "eks" {
  source  = "./eks"
  project = var.project
  region  = var.region

  vpc_id          = module.vpc.vpc_id
  public_subnets  = module.vpc.public_subnets  # <-- ДОДАЛИ
  private_subnets = module.vpc.private_subnets # (може лишатись, але не використовується)

  depends_on = [module.vpc]
}