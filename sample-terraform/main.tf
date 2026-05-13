module "vpc" {
  source = "./modules/vpc"
  
  vpc_cidr = var.vpc_cidr
  region   = var.aws_region
  
  tags = {
    Name = "${var.project_name}-vpc"
  }
}

module "subnets" {
  source = "./modules/subnets"
  
  vpc_id            = module.vpc.vpc_id
  public_subnets   = var.public_subnets
  private_subnets  = var.private_subnets
  
  tags = {
    Name = "${var.project_name}-subnets"
  }
}

resource "aws_security_group" "main" {
  name_prefix = var.project_name
  description = "Main security group"
  vpc_id      = module.vpc.vpc_id
  
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  
  tags = {
    Name = "${var.project_name}-sg"
  }
}

resource "aws_lb" "main" {
  name_prefix        = "lb"
  internal           = false
  load_balancer_type = "application"
  subnets            = module.subnets.public_subnet_ids
  
  enable_deletion_protection = false
  
  tags = {
    Name = "${var.project_name}-alb"
  }
}

resource "aws_autoscaling_group" "main" {
  name                = "${var.project_name}-asg"
  vpc_zone_identifier = module.subnets.private_subnet_ids
  min_size            = var.asg_min_size
  max_size            = var.asg_max_size
  desired_capacity    = var.asg_desired_capacity
  
  launch_template {
    id      = aws_launch_template.main.id
    version = "$Latest"
  }
}

resource "aws_launch_template" "main" {
  name_prefix   = "lt-"
  image_id      = data.aws_ami.amazon_linux_2.id
  instance_type = var.instance_type
  
  iam_instance_profile {
    name = aws_iam_instance_profile.main.name
  }
  
  vpc_security_group_ids = [aws_security_group.main.id]
}

resource "aws_iam_role" "main" {
  name_prefix = "role-"
  
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "ec2.amazonaws.com"
        }
      }
    ]
  })
}

resource "aws_iam_instance_profile" "main" {
  name_prefix = "profile-"
  role        = aws_iam_role.main.name
}

resource "aws_iam_role_policy_attachment" "ssm" {
  role       = aws_iam_role.main.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

data "aws_ami" "amazon_linux_2" {
  most_recent = true
  owners      = ["amazon"]
  
  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}

output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "load_balancer_dns" {
  description = "Load Balancer DNS"
  value       = aws_lb.main.dns_name
}

output "asg_name" {
  description = "Auto Scaling Group Name"
  value       = aws_autoscaling_group.main.name
}
