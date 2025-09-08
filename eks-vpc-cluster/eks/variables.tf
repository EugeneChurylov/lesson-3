variable "project" {}
variable "region"  {}

# Беремо значення з root (без remote_state, щоб не потрібен був S3)
variable "vpc_id"          { type = string }
variable "private_subnets" { type = list(string) }
variable "public_subnets" { type = list(string) }