variable "project_name" {
    description = "Project name prefix for resources"
    type = string
    default = "mlops-train-automation"
}


variable "aws_region" {
    description = "AWS region"
    type = string
    default = "eu-central-1"
}
