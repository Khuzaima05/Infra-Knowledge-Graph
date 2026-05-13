"""Tests for Repository Ingestion Service

Unit tests for GitHub repository ingestion functionality.
"""

import pytest
from pathlib import Path
from services.repo_ingestion_service import (
    RepoIngestionService,
    RepositoryValidationError,
    RepositoryIngestionError
)


class TestRepoIngestionService:
    """Test suite for RepoIngestionService"""
    
    @pytest.fixture
    def service(self, tmp_path):
        """Create a service instance with temporary workspace"""
        return RepoIngestionService(workspace_dir=str(tmp_path / "test_repos"))
    
    # URL Validation Tests
    
    def test_validate_github_url_https(self, service):
        """Test validation of HTTPS GitHub URLs"""
        valid_urls = [
            "https://github.com/owner/repo",
            "https://github.com/owner/repo.git",
            "https://github.com/owner/repo/",
            "https://github.com/owner-name/repo-name",
        ]
        for url in valid_urls:
            assert service.validate_github_url(url), f"Should validate: {url}"
    
    def test_validate_github_url_ssh(self, service):
        """Test validation of SSH GitHub URLs"""
        valid_urls = [
            "git@github.com:owner/repo",
            "git@github.com:owner/repo.git",
        ]
        for url in valid_urls:
            assert service.validate_github_url(url), f"Should validate: {url}"
    
    def test_validate_github_url_invalid(self, service):
        """Test rejection of invalid URLs"""
        invalid_urls = [
            "https://gitlab.com/owner/repo",
            "https://github.com/owner",
            "not-a-url",
            "",
            "ftp://github.com/owner/repo",
        ]
        for url in invalid_urls:
            assert not service.validate_github_url(url), f"Should reject: {url}"
    
    # URL Parsing Tests
    
    def test_parse_github_url_https(self, service):
        """Test parsing HTTPS GitHub URLs"""
        url = "https://github.com/terraform-aws-modules/terraform-aws-vpc"
        result = service.parse_github_url(url)
        
        assert result['owner'] == "terraform-aws-modules"
        assert result['name'] == "terraform-aws-vpc"
        assert result['url'] == "https://github.com/terraform-aws-modules/terraform-aws-vpc"
    
    def test_parse_github_url_ssh(self, service):
        """Test parsing SSH GitHub URLs"""
        url = "git@github.com:hashicorp/terraform.git"
        result = service.parse_github_url(url)
        
        assert result['owner'] == "hashicorp"
        assert result['name'] == "terraform"
        assert result['url'] == "https://github.com/hashicorp/terraform"
    
    def test_parse_github_url_with_git_extension(self, service):
        """Test parsing URLs with .git extension"""
        url = "https://github.com/owner/repo.git"
        result = service.parse_github_url(url)
        
        assert result['name'] == "repo"
        assert not result['name'].endswith('.git')
    
    def test_parse_github_url_invalid(self, service):
        """Test parsing invalid URLs raises error"""
        with pytest.raises(RepositoryValidationError):
            service.parse_github_url("https://gitlab.com/owner/repo")
        
        with pytest.raises(RepositoryValidationError):
            service.parse_github_url("not-a-url")
    
    # Local Path Tests
    
    def test_get_local_path(self, service):
        """Test local path generation"""
        path = service.get_local_path("owner", "repo")
        
        assert isinstance(path, Path)
        assert str(path).endswith("owner/repo")
    
    def test_repository_exists_false(self, service):
        """Test repository existence check when not cloned"""
        exists = service.repository_exists("nonexistent", "repo")
        assert not exists
    
    # Terraform File Scanning Tests
    
    def test_find_terraform_files_empty(self, service, tmp_path):
        """Test scanning empty repository"""
        # Create empty repo structure
        repo_path = tmp_path / "test_repos" / "owner" / "repo"
        repo_path.mkdir(parents=True)
        (repo_path / ".git").mkdir()
        
        files = service.find_terraform_files("owner", "repo")
        assert files == []
    
    def test_find_terraform_files_with_files(self, service, tmp_path):
        """Test scanning repository with Terraform files"""
        # Create repo with Terraform files
        repo_path = tmp_path / "test_repos" / "owner" / "repo"
        repo_path.mkdir(parents=True)
        (repo_path / ".git").mkdir()
        
        # Create test files
        (repo_path / "main.tf").write_text("resource \"aws_vpc\" \"main\" {}")
        (repo_path / "variables.tf").write_text("variable \"region\" {}")
        (repo_path / "terraform.tfvars").write_text("region = \"us-east-1\"")
        (repo_path / "README.md").write_text("# Test")
        
        # Create subdirectory with more files
        modules_dir = repo_path / "modules" / "vpc"
        modules_dir.mkdir(parents=True)
        (modules_dir / "main.tf").write_text("resource \"aws_subnet\" \"main\" {}")
        
        files = service.find_terraform_files("owner", "repo")
        
        assert len(files) == 4
        assert "main.tf" in files
        assert "variables.tf" in files
        assert "terraform.tfvars" in files
        assert "modules/vpc/main.tf" in files
        assert "README.md" not in files
    
    def test_find_terraform_files_excludes_terraform_dir(self, service, tmp_path):
        """Test that .terraform directory is excluded"""
        repo_path = tmp_path / "test_repos" / "owner" / "repo"
        repo_path.mkdir(parents=True)
        (repo_path / ".git").mkdir()
        
        # Create file in .terraform directory (should be excluded)
        terraform_dir = repo_path / ".terraform" / "providers"
        terraform_dir.mkdir(parents=True)
        (terraform_dir / "provider.tf").write_text("# Should be excluded")
        
        # Create normal file
        (repo_path / "main.tf").write_text("resource \"aws_vpc\" \"main\" {}")
        
        files = service.find_terraform_files("owner", "repo")
        
        assert len(files) == 1
        assert "main.tf" in files
        assert ".terraform" not in str(files)
    
    def test_find_terraform_files_nonexistent_repo(self, service):
        """Test scanning nonexistent repository raises error"""
        with pytest.raises(RepositoryIngestionError):
            service.find_terraform_files("nonexistent", "repo")
    
    # File Content Tests
    
    def test_get_terraform_file_content(self, service, tmp_path):
        """Test reading Terraform file content"""
        repo_path = tmp_path / "test_repos" / "owner" / "repo"
        repo_path.mkdir(parents=True)
        
        content = 'resource "aws_vpc" "main" {\n  cidr_block = "10.0.0.0/16"\n}'
        (repo_path / "main.tf").write_text(content)
        
        path, read_content = service.get_terraform_file_content("owner", "repo", "main.tf")
        
        assert path == "main.tf"
        assert read_content == content
    
    def test_get_terraform_file_content_nonexistent(self, service, tmp_path):
        """Test reading nonexistent file raises error"""
        repo_path = tmp_path / "test_repos" / "owner" / "repo"
        repo_path.mkdir(parents=True)
        
        with pytest.raises(RepositoryIngestionError):
            service.get_terraform_file_content("owner", "repo", "nonexistent.tf")
    
    def test_get_terraform_file_content_path_traversal(self, service, tmp_path):
        """Test path traversal protection"""
        repo_path = tmp_path / "test_repos" / "owner" / "repo"
        repo_path.mkdir(parents=True)
        
        with pytest.raises(RepositoryIngestionError):
            service.get_terraform_file_content("owner", "repo", "../../etc/passwd")
    
    # Cleanup Tests
    
    def test_delete_repository(self, service, tmp_path):
        """Test repository deletion"""
        repo_path = tmp_path / "test_repos" / "owner" / "repo"
        repo_path.mkdir(parents=True)
        (repo_path / ".git").mkdir()
        (repo_path / "main.tf").write_text("resource \"aws_vpc\" \"main\" {}")
        
        assert repo_path.exists()
        
        deleted = service.delete_repository("owner", "repo")
        
        assert deleted
        assert not repo_path.exists()
    
    def test_delete_repository_nonexistent(self, service):
        """Test deleting nonexistent repository returns False"""
        deleted = service.delete_repository("nonexistent", "repo")
        assert not deleted
    
    # Storage Tests
    
    def test_get_storage_usage_empty(self, service):
        """Test storage usage for empty workspace"""
        usage = service.get_storage_usage()
        
        assert usage['total_bytes'] >= 0
        assert usage['total_mb'] >= 0
        assert usage['repositories'] == 0
    
    def test_get_storage_usage_with_repos(self, service, tmp_path):
        """Test storage usage calculation"""
        # Create test repository
        repo_path = tmp_path / "test_repos" / "owner" / "repo"
        repo_path.mkdir(parents=True)
        (repo_path / ".git").mkdir()
        (repo_path / "main.tf").write_text("resource \"aws_vpc\" \"main\" {}" * 100)
        
        usage = service.get_storage_usage()
        
        assert usage['total_bytes'] > 0
        assert usage['total_mb'] > 0
        assert usage['repositories'] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

# Made with Bob
