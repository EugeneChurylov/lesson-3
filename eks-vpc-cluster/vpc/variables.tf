variable "project" {}
variable "cidr"    { default = "10.0.0.0/16" }
variable "azs"     { type = list(string) }
variable "public_subnets"  { type = list(string) }
variable "private_subnets" { type = list(string) }