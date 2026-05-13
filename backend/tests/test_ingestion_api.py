"""API Integration Tests for Repository Ingestion

Tests for the FastAPI ingestion endpoints.
"""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import shutil


@pytest.fixture
def test_workspace(tmp_path):
    """Create temporary workspace for testing"""
    workspace = tmp_path / "test_repos"
    workspace.mkdir()
    yield workspace
    # Cleanup
    if workspace.exists():
        shutil.rmtree(workspace)


@pytest.fixture
def client(test_workspace, monkeypatch):
    """Create test client with mocked workspace"""
    # Mock the workspace directory
    monkeypatch.setenv("TF_WORKSPACE_DIR", str(test_workspace))
    
    from app.main import app
    return TestClient(app)


class TestIngestionEndpoints:
    """Test suite for ingestion API endpoints"""
    
    def test_validate_url_valid_https(self, client):
        """Test URL validation with valid HTTPS URL"""
        response = client.post(
            "/api/ingestion/validate",
            params={"url": "https://github.com/terraform-aws-modules/terraform-aws-vpc"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['valid'] is True
        assert data['owner'] == "terraform-aws-modules"
        assert data['name'] == "terraform-aws-vpc"
    
    def test_validate_url_valid_ssh(self, client):
        """Test URL validation with valid SSH URL"""
        response = client.post(
            "/api/ingestion/validate",
            params={"url": "git@github.com:hashicorp/terraform.git"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data['valid'] is True
        assert data['owner'] == "hashicorp"
        assert data['name'] == "terraform"
    
    def test_validate_url_invalid(self, client):
        """Test URL validation with invalid URL"""
        response = client.post(
            "/api/ingestion/validate",
            params={"url": "https://gitlab.com/owner/repo"}
        )
        
        assert response.status_code == 400
        assert "Invalid GitHub URL" in response.json()['detail']
    
    def test_check_repository_exists_false(self, client):
        """Test checking nonexistent repository"""
        response = client.get("/api/ingestion/owner/repo/exists")
        
        assert response.status_code == 200
        data = response.json()
        assert data['exists'] is False
        assert data['owner'] == "owner"
        assert data['name'] == "repo"
    
    def test_get_storage_usage(self, client):
        """Test getting storage usage"""
        response = client.get("/api/ingestion/storage")
        
        assert response.status_code == 200
        data = response.json()
        assert 'total_bytes' in data
        assert 'total_mb' in data
        assert 'repositories' in data
        assert data['repositories'] >= 0
    
    def test_get_terraform_files_nonexistent_repo(self, client):
        """Test getting Terraform files from nonexistent repository"""
        response = client.get("/api/ingestion/terraform-files/owner/repo")
        
        assert response.status_code == 404
        assert "not found" in response.json()['detail'].lower()
    
    def test_delete_repository_nonexistent(self, client):
        """Test deleting nonexistent repository"""
        response = client.delete("/api/ingestion/owner/repo")
        
        assert response.status_code == 404
        assert "not found" in response.json()['detail'].lower()
    
    def test_cleanup_old_repositories(self, client):
        """Test cleanup endpoint"""
        response = client.post(
            "/api/ingestion/cleanup",
            params={"max_age_days": 30}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert 'checked' in data
        assert 'deleted' in data
        assert 'errors' in data


class TestIngestionWorkflow:
    """Test complete ingestion workflow"""
    
    def test_full_workflow_with_mock_repo(self, client, test_workspace):
        """Test complete workflow with a mock repository"""
        # Create a mock repository structure
        repo_path = test_workspace / "test-owner" / "test-repo"
        repo_path.mkdir(parents=True)
        (repo_path / ".git").mkdir()
        
        # Create Terraform files
        (repo_path / "main.tf").write_text('resource "aws_vpc" "main" {}')
        (repo_path / "variables.tf").write_text('variable "region" {}')
        
        # Check repository exists
        response = client.get("/api/ingestion/test-owner/test-repo/exists")
        assert response.status_code == 200
        assert response.json()['exists'] is True
        
        # Get Terraform files
        response = client.get("/api/ingestion/terraform-files/test-owner/test-repo")
        assert response.status_code == 200
        data = response.json()
        assert data['total_files'] == 2
        assert "main.tf" in data['terraform_files']
        assert "variables.tf" in data['terraform_files']
        
        # Get file content
        response = client.get("/api/ingestion/terraform-files/test-owner/test-repo/main.tf")
        assert response.status_code == 200
        data = response.json()
        assert data['file_path'] == "main.tf"
        assert 'aws_vpc' in data['content']
        
        # Check storage usage
        response = client.get("/api/ingestion/storage")
        assert response.status_code == 200
        data = response.json()
        assert data['repositories'] >= 1
        assert data['total_bytes'] > 0
        
        # Delete repository
        response = client.delete("/api/ingestion/test-owner/test-repo")
        assert response.status_code == 200
        assert response.json()['success'] is True
        
        # Verify deletion
        response = client.get("/api/ingestion/test-owner/test-repo/exists")
        assert response.status_code == 200
        assert response.json()['exists'] is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

# Made with Bob
