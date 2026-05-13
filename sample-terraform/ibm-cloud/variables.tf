##############################################################################
# Input Variables
##############################################################################

variable "ibmcloud_api_key" {
  description = "IBM Cloud API key"
  type        = string
  sensitive   = true
}

variable "region" {
  description = "IBM Cloud region where resources will be created"
  type        = string
  default     = "us-south"
}

variable "resource_group_name" {
  description = "Name of the resource group"
  type        = string
  default     = "default"
}

variable "prefix" {
  description = "Prefix for all resource names"
  type        = string
  default     = "demo"
  
  validation {
    condition     = length(var.prefix) <= 16
    error_message = "Prefix must be 16 characters or less."
  }
}

variable "tags" {
  description = "List of tags to apply to resources"
  type        = list(string)
  default     = ["terraform", "demo", "infrastructure-kg"]
}

variable "worker_pools_taints" {
  description = "Taints for worker pools"
  type        = map(list(object({
    key    = string
    value  = string
    effect = string
  })))
  default = {}
}

variable "activity_tracker_crn" {
  description = "CRN of Activity Tracker instance"
  type        = string
  default     = null
}