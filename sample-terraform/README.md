# Sample Terraform Configuration

This is a sample Terraform configuration used for testing the Infra Knowledge Graph.

## What's Included

- **VPC Module**: Creates a VPC with customizable CIDR blocks
- **Subnets Module**: Creates public and private subnets
- **Security Group**: Main security group for load balancer
- **Application Load Balancer**: Distributes traffic to ASG
- **Auto Scaling Group**: Manages EC2 instances
- **IAM Role & Instance Profile**: Permissions for EC2 instances

## Resources Created

- 1 VPC
- 2 Public Subnets
- 2 Private Subnets
- 1 Application Load Balancer
- 1 Auto Scaling Group
- 1 Launch Template
- 1 Security Group
- 1 IAM Role
- 1 IAM Instance Profile

## Variables

- `aws_region`: AWS region (default: us-east-1)
- `project_name`: Project name (default: demo-project)
- `vpc_cidr`: VPC CIDR block (default: 10.0.0.0/16)
- `instance_type`: EC2 instance type (default: t3.micro)
- `asg_min_size`: Min ASG size
- `asg_max_size`: Max ASG size
- `asg_desired_capacity`: Desired ASG capacity

## Outputs

- `vpc_id`: The VPC ID
- `load_balancer_dns`: The load balancer DNS name
- `asg_name`: The Auto Scaling Group name
