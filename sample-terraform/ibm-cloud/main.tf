##############################################################################
# IBM Cloud Infrastructure Example
# 
# This example demonstrates a typical IBM Cloud infrastructure setup using
# terraform-ibm-modules for VPC, IKS cluster, and supporting services.
##############################################################################

terraform {
  required_version = ">= 1.3.0"
  required_providers {
    ibm = {
      source  = "IBM-Cloud/ibm"
      version = ">= 1.60.0"
    }
  }
}

##############################################################################
# Provider Configuration
##############################################################################

provider "ibm" {
  ibmcloud_api_key = var.ibmcloud_api_key
  region           = var.region
}

##############################################################################
# Resource Group
##############################################################################

data "ibm_resource_group" "resource_group" {
  name = var.resource_group_name
}

##############################################################################
# VPC Module
##############################################################################

module "vpc" {
  source  = "terraform-ibm-modules/landing-zone-vpc/ibm"
  version = "7.18.3"

  resource_group_id = data.ibm_resource_group.resource_group.id
  region            = var.region
  prefix            = var.prefix
  name              = "${var.prefix}-vpc"
  tags              = var.tags

  # Subnets configuration
  subnets = {
    zone-1 = [
      {
        name           = "subnet-a"
        cidr           = "10.10.10.0/24"
        public_gateway = true
      }
    ],
    zone-2 = [
      {
        name           = "subnet-b"
        cidr           = "10.20.10.0/24"
        public_gateway = true
      }
    ],
    zone-3 = [
      {
        name           = "subnet-c"
        cidr           = "10.30.10.0/24"
        public_gateway = true
      }
    ]
  }

  use_public_gateways = {
    zone-1 = true
    zone-2 = true
    zone-3 = true
  }

  # Security groups
  security_group_rules = [
    {
      name      = "allow-inbound-ping"
      direction = "inbound"
      remote    = "0.0.0.0/0"
      icmp = {
        type = 8
      }
    },
    {
      name      = "allow-inbound-ssh"
      direction = "inbound"
      remote    = "0.0.0.0/0"
      tcp = {
        port_min = 22
        port_max = 22
      }
    }
  ]
}

##############################################################################
# IKS Cluster Module
##############################################################################

module "iks_cluster" {
  source  = "terraform-ibm-modules/iks/ibm"
  version = "1.2.0"

  cluster_name              = "${var.prefix}-iks-cluster"
  resource_group_id         = data.ibm_resource_group.resource_group.id
  region                    = var.region
  force_delete_storage      = true
  vpc_id                    = module.vpc.vpc_id
  worker_pools_taints       = var.worker_pools_taints
  tags                      = var.tags
  cluster_ready_when        = "IngressReady"
  ignore_worker_pool_size_changes = true

  worker_pools = [
    {
      subnet_prefix     = "subnet"
      pool_name         = "default"
      machine_type      = "bx2.4x16"
      workers_per_zone  = 2
      resource_group_id = data.ibm_resource_group.resource_group.id
    }
  ]

  depends_on = [module.vpc]
}

##############################################################################
# Cloud Object Storage Module
##############################################################################

module "cos" {
  source  = "terraform-ibm-modules/cos/ibm"
  version = "8.5.3"

  resource_group_id = data.ibm_resource_group.resource_group.id
  region            = var.region
  cos_instance_name = "${var.prefix}-cos"
  cos_tags          = var.tags
  bucket_name       = "${var.prefix}-bucket"
  retention_enabled = false
  kms_encryption_enabled = false

  # Bucket configuration
  bucket_storage_class = "smart"
  object_versioning_enabled = true
  
  # Activity tracking
  activity_tracker_crn = var.activity_tracker_crn
}

##############################################################################
# Key Protect Module
##############################################################################

module "key_protect" {
  source  = "terraform-ibm-modules/key-protect/ibm"
  version = "2.3.0"

  resource_group_id  = data.ibm_resource_group.resource_group.id
  region             = var.region
  key_protect_name   = "${var.prefix}-kp"
  tags               = var.tags
}

##############################################################################
# Security Group Module
##############################################################################

module "security_group" {
  source  = "terraform-ibm-modules/security-group/ibm"
  version = "2.6.2"

  security_group_name = "${var.prefix}-sg"
  resource_group      = data.ibm_resource_group.resource_group.id
  vpc_id              = module.vpc.vpc_id
  tags                = var.tags

  security_group_rules = [
    {
      name      = "allow-all-outbound"
      direction = "outbound"
      remote    = "0.0.0.0/0"
    },
    {
      name      = "allow-https-inbound"
      direction = "inbound"
      remote    = "0.0.0.0/0"
      tcp = {
        port_min = 443
        port_max = 443
      }
    },
    {
      name      = "allow-http-inbound"
      direction = "inbound"
      remote    = "0.0.0.0/0"
      tcp = {
        port_min = 80
        port_max = 80
      }
    }
  ]

  depends_on = [module.vpc]
}

##############################################################################
# VPN Gateway Module
##############################################################################

module "vpn_gateway" {
  source  = "terraform-ibm-modules/vpn-gateway/ibm"
  version = "1.3.0"

  vpn_gateway_name  = "${var.prefix}-vpn"
  resource_group_id = data.ibm_resource_group.resource_group.id
  subnet_id         = module.vpc.subnet_zone_list[0].id
  mode              = "route"
  tags              = var.tags

  depends_on = [module.vpc]
}