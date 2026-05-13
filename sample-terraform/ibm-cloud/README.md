# IBM Cloud Infrastructure Example

This example demonstrates a complete IBM Cloud infrastructure setup using official terraform-ibm-modules.

## Architecture

This configuration creates:

- **VPC**: Multi-zone VPC with public gateways
- **IKS Cluster**: IBM Kubernetes Service cluster with worker pools
- **Cloud Object Storage**: COS instance with bucket
- **Key Protect**: Key management service
- **Security Groups**: Network security rules
- **VPN Gateway**: VPN connectivity

## Modules Used

All modules are from the official [terraform-ibm-modules](https://github.com/terraform-ibm-modules) organization:

- `terraform-ibm-modules/landing-zone-vpc/ibm` - VPC infrastructure
- `terraform-ibm-modules/iks/ibm` - Kubernetes cluster
- `terraform-ibm-modules/cos/ibm` - Object storage
- `terraform-ibm-modules/key-protect/ibm` - Key management
- `terraform-ibm-modules/security-group/ibm` - Security groups
- `terraform-ibm-modules/vpn-gateway/ibm` - VPN gateway

## Prerequisites

1. IBM Cloud account
2. IBM Cloud API key
3. Terraform >= 1.3.0

## Usage

### 1. Set IBM Cloud API Key

```bash
export TF_VAR_ibmcloud_api_key="your-api-key-here"
```

### 2. Initialize Terraform

```bash
terraform init
```

### 3. Review Plan

```bash
terraform plan
```

### 4. Apply Configuration

```bash
terraform apply
```

## Variables

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|----------|
| ibmcloud_api_key | IBM Cloud API key | string | - | yes |
| region | IBM Cloud region | string | us-south | no |
| resource_group_name | Resource group name | string | default | no |
| prefix | Prefix for resource names | string | demo | no |
| tags | Tags for resources | list(string) | ["terraform", "demo"] | no |

## Outputs

| Name | Description |
|------|-------------|
| vpc_id | VPC ID |
| vpc_crn | VPC CRN |
| subnet_ids | List of subnet IDs |
| iks_cluster_id | IKS cluster ID |
| iks_cluster_name | IKS cluster name |
| iks_ingress_hostname | IKS ingress hostname |
| cos_instance_id | COS instance ID |
| cos_bucket_name | COS bucket name |
| key_protect_instance_id | Key Protect instance ID |
| security_group_id | Security group ID |
| vpn_gateway_id | VPN gateway ID |
| vpn_gateway_public_ip | VPN gateway public IP |

## Analyzing with Infrastructure Knowledge Graph

To analyze this infrastructure with the Knowledge Graph tool:

1. Push this code to a GitHub repository
2. Open the Infrastructure Knowledge Graph application
3. Enter your repository URL
4. Click "Analyze Repository"
5. View the dependency graph showing:
   - VPC and subnet relationships
   - IKS cluster dependencies
   - COS and Key Protect connections
   - Security group rules
   - VPN gateway configuration

## Resource Dependencies

```
Resource Group
    ├── VPC
    │   ├── Subnets (3 zones)
    │   ├── Public Gateways
    │   └── Security Groups
    ├── IKS Cluster
    │   └── Worker Pools (depends on VPC subnets)
    ├── Cloud Object Storage
    │   └── Bucket
    ├── Key Protect
    │   └── Keys
    ├── Security Group
    │   └── Rules
    └── VPN Gateway
        └── Connections
```

## Cost Estimate

Approximate monthly costs (us-south region):
- VPC: Free
- IKS Cluster (2 workers, bx2.4x16): ~$300/month
- COS (Standard): ~$0.023/GB
- Key Protect: ~$1/key/month
- VPN Gateway: ~$0.045/hour (~$33/month)

**Total**: ~$335-400/month (varies by usage)

## Cleanup

To destroy all resources:

```bash
terraform destroy
```

## More Examples

Explore more IBM Cloud Terraform modules:
- https://github.com/terraform-ibm-modules/terraform-ibm-landing-zone-vpc
- https://github.com/terraform-ibm-modules/terraform-ibm-iks
- https://github.com/terraform-ibm-modules/terraform-ibm-cos
- https://github.com/terraform-ibm-modules/terraform-ibm-key-protect
- https://github.com/terraform-ibm-modules/terraform-ibm-security-group
- https://github.com/terraform-ibm-modules/terraform-ibm-vpn-gateway