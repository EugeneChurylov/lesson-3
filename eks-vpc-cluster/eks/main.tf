locals { cluster_version = "1.29" }

module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.0"

  cluster_name    = "${var.project}-eks"
  cluster_version = local.cluster_version

  vpc_id     = var.vpc_id
  # ВАЖЛИВО: запускаємо ноди у ПУБЛІЧНИХ сабнетах
  subnet_ids = var.public_subnets

  cluster_endpoint_public_access = true
  # cluster_endpoint_private_access = false  # за замовчуванням і так false

  enable_cluster_creator_admin_permissions = true

  eks_managed_node_groups = {
    cpu = {
      instance_types = ["t3.medium"]  # можна t3.small
      desired_size   = 1
      min_size       = 1
      max_size       = 2
      labels         = { role = "cpu" }
    }
    gpu = {
      instance_types = ["g4dn.xlarge"]
      desired_size   = 0
      min_size       = 0
      max_size       = 1
      ami_type       = "AL2_x86_64_GPU"
      labels         = { role = "gpu" }
    }
  }

  tags = { Project = var.project }
}
