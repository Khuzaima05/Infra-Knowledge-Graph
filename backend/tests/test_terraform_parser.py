"""Unit tests for Terraform Parser

Tests for parsing Terraform files and extracting components.
"""

import pytest
import tempfile
import os
from pathlib import Path

from parser.terraform_parser_v2 import TerraformParser
from parser.parser_schemas import ParserConfig, RepositoryParseResult
from parser.parser_utils import (
    normalize_value,
    extract_provider_from_resource_type,
    detect_variable_references,
    detect_module_references,
    detect_resource_references
)


class TestParserUtils:
    """Test utility functions"""
    
    def test_normalize_value_primitives(self):
        """Test normalization of primitive values"""
        assert normalize_value("string") == "string"
        assert normalize_value(42) == 42
        assert normalize_value(3.14) == 3.14
        assert normalize_value(True) is True
        assert normalize_value(None) is None
    
    def test_normalize_value_collections(self):
        """Test normalization of collections"""
        assert normalize_value([1, 2, 3]) == [1, 2, 3]
        assert normalize_value({"key": "value"}) == {"key": "value"}
        assert normalize_value([{"a": 1}, {"b": 2}]) == [{"a": 1}, {"b": 2}]
    
    def test_extract_provider_from_resource_type(self):
        """Test provider extraction from resource types"""
        assert extract_provider_from_resource_type("aws_vpc") == "aws"
        assert extract_provider_from_resource_type("azurerm_virtual_network") == "azurerm"
        assert extract_provider_from_resource_type("google_compute_network") == "google"
        assert extract_provider_from_resource_type("") == "unknown"
    
    def test_detect_variable_references(self):
        """Test variable reference detection"""
        content = """
        resource "aws_vpc" "main" {
          cidr_block = var.vpc_cidr
          tags = {
            Name = var.project_name
          }
        }
        """
        refs = detect_variable_references(content)
        assert len(refs) == 2
        assert any(r['target'] == 'vpc_cidr' for r in refs)
        assert any(r['target'] == 'project_name' for r in refs)
    
    def test_detect_module_references(self):
        """Test module reference detection"""
        content = """
        resource "aws_subnet" "main" {
          vpc_id = module.vpc.vpc_id
          cidr_block = module.network.subnet_cidr
        }
        """
        refs = detect_module_references(content)
        assert len(refs) == 2
        assert any(r['module'] == 'vpc' and r['output'] == 'vpc_id' for r in refs)
        assert any(r['module'] == 'network' and r['output'] == 'subnet_cidr' for r in refs)
    
    def test_detect_resource_references(self):
        """Test resource reference detection"""
        content = """
        resource "aws_subnet" "main" {
          vpc_id = aws_vpc.main.id
          security_group_ids = [aws_security_group.main.id]
        }
        """
        refs = detect_resource_references(content)
        assert len(refs) >= 2
        assert any(r['resource_type'] == 'aws_vpc' and r['resource_name'] == 'main' for r in refs)


class TestTerraformParser:
    """Test Terraform parser functionality"""
    
    @pytest.fixture
    def parser(self):
        """Create parser instance"""
        return TerraformParser()
    
    @pytest.fixture
    def temp_repo(self):
        """Create temporary repository with Terraform files"""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            
            # Create main.tf
            main_tf = repo_path / "main.tf"
            main_tf.write_text("""
resource "aws_vpc" "main" {
  cidr_block = var.vpc_cidr
  
  tags = {
    Name = "main-vpc"
  }
}

resource "aws_subnet" "public" {
  vpc_id     = aws_vpc.main.id
  cidr_block = "10.0.1.0/24"
}

module "vpc" {
  source  = "./modules/vpc"
  version = "1.0.0"
  
  vpc_cidr = var.vpc_cidr
}

output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}
""")
            
            # Create variables.tf
            variables_tf = repo_path / "variables.tf"
            variables_tf.write_text("""
variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
  sensitive   = false
}
""")
            
            # Create provider.tf
            provider_tf = repo_path / "provider.tf"
            provider_tf.write_text("""
terraform {
  required_version = ">= 1.0"
  
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region
}
""")
            
            # Create locals.tf
            locals_tf = repo_path / "locals.tf"
            locals_tf.write_text("""
locals {
  common_tags = {
    Environment = "dev"
    Project     = "test"
  }
  
  vpc_name = "main-vpc"
}
""")
            
            # Create data.tf
            data_tf = repo_path / "data.tf"
            data_tf.write_text("""
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]
  
  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*"]
  }
}
""")
            
            yield str(repo_path)
    
    def test_find_terraform_files(self, parser, temp_repo):
        """Test finding Terraform files"""
        files = parser.find_terraform_files(temp_repo)
        
        assert len(files) == 5
        assert any('main.tf' in f for f in files)
        assert any('variables.tf' in f for f in files)
        assert any('provider.tf' in f for f in files)
        assert any('locals.tf' in f for f in files)
        assert any('data.tf' in f for f in files)
    
    def test_parse_resources(self, parser, temp_repo):
        """Test parsing resources"""
        result = parser.parse_repository(temp_repo)
        
        assert result.status in ["success", "partial"]
        assert len(result.resources) >= 2
        
        # Check VPC resource
        vpc = next((r for r in result.resources if r.name == "main" and r.type == "aws_vpc"), None)
        assert vpc is not None
        assert vpc.provider == "aws"
        assert vpc.full_name == "aws_vpc.main"
        assert "cidr_block" in vpc.metadata
    
    def test_parse_modules(self, parser, temp_repo):
        """Test parsing modules"""
        result = parser.parse_repository(temp_repo)
        
        assert len(result.modules) >= 1
        
        vpc_module = next((m for m in result.modules if m.name == "vpc"), None)
        assert vpc_module is not None
        assert vpc_module.source == "./modules/vpc"
        assert vpc_module.version == "1.0.0"
    
    def test_parse_variables(self, parser, temp_repo):
        """Test parsing variables"""
        result = parser.parse_repository(temp_repo)
        
        assert len(result.variables) >= 2
        
        vpc_cidr_var = next((v for v in result.variables if v.name == "vpc_cidr"), None)
        assert vpc_cidr_var is not None
        assert vpc_cidr_var.type == "string"
        assert vpc_cidr_var.default_value == "10.0.0.0/16"
        assert "VPC CIDR" in vpc_cidr_var.description
        
        region_var = next((v for v in result.variables if v.name == "region"), None)
        assert region_var is not None
        assert region_var.sensitive is False
    
    def test_parse_outputs(self, parser, temp_repo):
        """Test parsing outputs"""
        result = parser.parse_repository(temp_repo)
        
        assert len(result.outputs) >= 1
        
        vpc_id_output = next((o for o in result.outputs if o.name == "vpc_id"), None)
        assert vpc_id_output is not None
        assert "VPC ID" in vpc_id_output.description
    
    def test_parse_providers(self, parser, temp_repo):
        """Test parsing providers"""
        result = parser.parse_repository(temp_repo)
        
        assert len(result.providers) >= 1
        
        aws_provider = next((p for p in result.providers if p.name == "aws"), None)
        assert aws_provider is not None
        assert aws_provider.version == "~> 5.0"
        assert aws_provider.source == "hashicorp/aws"
    
    def test_parse_locals(self, parser, temp_repo):
        """Test parsing local values"""
        result = parser.parse_repository(temp_repo)
        
        assert len(result.locals) >= 2
        
        common_tags = next((l for l in result.locals if l.name == "common_tags"), None)
        assert common_tags is not None
        assert isinstance(common_tags.value, dict)
        
        vpc_name = next((l for l in result.locals if l.name == "vpc_name"), None)
        assert vpc_name is not None
        assert vpc_name.value == "main-vpc"
    
    def test_parse_data_sources(self, parser, temp_repo):
        """Test parsing data sources"""
        result = parser.parse_repository(temp_repo)
        
        assert len(result.data_sources) >= 1
        
        ami_data = next((d for d in result.data_sources if d.name == "amazon_linux"), None)
        assert ami_data is not None
        assert ami_data.type == "aws_ami"
        assert ami_data.provider == "aws"
        assert ami_data.full_name == "data.aws_ami.amazon_linux"
    
    def test_parse_statistics(self, parser, temp_repo):
        """Test statistics calculation"""
        result = parser.parse_repository(temp_repo)
        
        assert result.statistics['total_resources'] == len(result.resources)
        assert result.statistics['total_modules'] == len(result.modules)
        assert result.statistics['total_variables'] == len(result.variables)
        assert result.statistics['total_outputs'] == len(result.outputs)
        assert result.statistics['total_providers'] == len(result.providers)
    
    def test_malformed_file_handling(self, parser):
        """Test handling of malformed Terraform files"""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            
            # Create malformed file
            bad_tf = repo_path / "bad.tf"
            bad_tf.write_text("""
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  # Missing closing brace
""")
            
            result = parser.parse_repository(str(repo_path))
            
            # Should handle error gracefully
            assert result.status in ["error", "partial"]
            assert result.failed_files >= 1
            assert len(result.errors) > 0
    
    def test_empty_repository(self, parser):
        """Test parsing empty repository"""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = parser.parse_repository(tmpdir)
            
            assert result.status == "error"
            assert result.total_files == 0
            assert "No Terraform files found" in result.errors
    
    def test_format_output(self, parser, temp_repo):
        """Test output formatting"""
        result = parser.parse_repository(temp_repo)
        formatted = parser.format_output(result)
        
        assert "resources" in formatted
        assert "modules" in formatted
        assert "variables" in formatted
        assert "outputs" in formatted
        assert "providers" in formatted
        assert "statistics" in formatted
        assert "status" in formatted
        
        assert isinstance(formatted["resources"], list)
        assert isinstance(formatted["statistics"], dict)
    
    def test_parser_config(self):
        """Test parser configuration"""
        config = ParserConfig(
            exclude_dirs=['.terraform', '.git', 'custom_dir'],
            max_file_size_mb=5,
            continue_on_error=False
        )
        
        parser = TerraformParser(config=config)
        
        assert parser.config.max_file_size_mb == 5
        assert parser.config.continue_on_error is False
        assert 'custom_dir' in parser.config.exclude_dirs


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

# Made with Bob
