##############################################################################
# Outputs
##############################################################################

output "vpc_id" {
  description = "ID of the VPC"
  value       = module.vpc.vpc_id
}

output "vpc_crn" {
  description = "CRN of the VPC"
  value       = module.vpc.vpc_crn
}

output "subnet_ids" {
  description = "IDs of all subnets"
  value       = [for subnet in module.vpc.subnet_zone_list : subnet.id]
}

output "iks_cluster_id" {
  description = "ID of the IKS cluster"
  value       = module.iks_cluster.cluster_id
}

output "iks_cluster_name" {
  description = "Name of the IKS cluster"
  value       = module.iks_cluster.cluster_name
}

output "iks_ingress_hostname" {
  description = "Ingress hostname for the IKS cluster"
  value       = module.iks_cluster.ingress_hostname
}

output "cos_instance_id" {
  description = "ID of the COS instance"
  value       = module.cos.cos_instance_id
}

output "cos_bucket_name" {
  description = "Name of the COS bucket"
  value       = module.cos.bucket_name
}

output "key_protect_instance_id" {
  description = "ID of the Key Protect instance"
  value       = module.key_protect.key_protect_id
}

output "security_group_id" {
  description = "ID of the security group"
  value       = module.security_group.security_group_id
}

output "vpn_gateway_id" {
  description = "ID of the VPN gateway"
  value       = module.vpn_gateway.vpn_gateway_id
}

output "vpn_gateway_public_ip" {
  description = "Public IP of the VPN gateway"
  value       = module.vpn_gateway.vpn_gateway_public_ip_address
}