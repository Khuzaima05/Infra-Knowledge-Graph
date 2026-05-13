"""Tests for Complete Analysis Workflow

Tests the end-to-end repository analysis orchestration.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.orm import Session

from services.analysis_orchestrator import AnalysisOrchestrator, AnalysisError
from parser.parser_schemas import (
    ParsedRepository, ParsedFile, ParsedResource, ParsedModule,
    ParsedVariable, ParsedOutput, ParsedProvider
)
from graph.graph_schemas import GraphResult, GraphNode, GraphEdge, GraphStatistics
from models.models import Repository


class TestAnalysisOrchestrator:
    """Test suite for AnalysisOrchestrator"""
    
    @pytest.fixture
    def mock_db(self):
        """Mock database session"""
        db = Mock(spec=Session)
        db.query.return_value.filter_by.return_value.first.return_value = None
        db.query.return_value.filter_by.return_value.count.return_value = 0
        return db
    
    @pytest.fixture
    def orchestrator(self, mock_db):
        """Create orchestrator instance"""
        return AnalysisOrchestrator(mock_db, workspace_dir="./test_repos")
    
    @pytest.fixture
    def sample_parsed_repo(self):
        """Sample parsed repository data"""
        return ParsedRepository(
            files=[
                ParsedFile(
                    path="main.tf",
                    content="resource \"aws_vpc\" \"main\" {}",
                    size=100
                )
            ],
            resources=[
                ParsedResource(
                    type="aws_vpc",
                    name="main",
                    provider="aws",
                    attributes={"cidr_block": "10.0.0.0/16"},
                    depends_on=[],
                    file_path="main.tf"
                )
            ],
            modules=[],
            variables=[],
            outputs=[],
            providers=[
                ParsedProvider(
                    name="aws",
                    version="~> 5.0",
                    alias=None,
                    configuration={"region": "us-east-1"},
                    file_path="provider.tf"
                )
            ],
            locals=[],
            data_sources=[]
        )
    
    @pytest.fixture
    def sample_graph_result(self):
        """Sample graph result"""
        return GraphResult(
            nodes=[
                GraphNode(
                    id="resource.aws_vpc.main",
                    type="resource",
                    label="aws_vpc.main",
                    data={"type": "aws_vpc", "name": "main"},
                    metadata={}
                )
            ],
            edges=[],
            statistics=GraphStatistics(
                total_nodes=1,
                total_edges=0,
                total_resources=1,
                total_modules=0,
                total_variables=0,
                total_outputs=0,
                total_providers=1
            )
        )
    
    def test_validate_url_success(self, orchestrator):
        """Test successful URL validation"""
        url = "https://github.com/owner/repo"
        result = orchestrator._validate_url(url)
        
        assert result['owner'] == 'owner'
        assert result['name'] == 'repo'
        assert result['url'] == url
    
    def test_validate_url_invalid(self, orchestrator):
        """Test invalid URL validation"""
        with pytest.raises(AnalysisError):
            orchestrator._validate_url("not-a-github-url")
    
    def test_get_or_create_repository_new(self, orchestrator, mock_db):
        """Test creating new repository record"""
        url = "https://github.com/owner/repo"
        branch = "main"
        repo_info = {'owner': 'owner', 'name': 'repo', 'url': url}
        
        repo = orchestrator._get_or_create_repository(url, branch, repo_info)
        
        assert repo.name == 'repo'
        assert repo.url == url
        assert repo.branch == branch
        assert repo.status == 'pending'
        mock_db.add.assert_called_once()
    
    def test_get_or_create_repository_existing(self, orchestrator, mock_db):
        """Test updating existing repository record"""
        url = "https://github.com/owner/repo"
        branch = "develop"
        repo_info = {'owner': 'owner', 'name': 'repo', 'url': url}
        
        existing_repo = Repository(
            id=1,
            name='repo',
            url=url,
            branch='main',
            status='completed'
        )
        mock_db.query.return_value.filter_by.return_value.first.return_value = existing_repo
        
        repo = orchestrator._get_or_create_repository(url, branch, repo_info)
        
        assert repo.id == 1
        assert repo.branch == branch
        mock_db.add.assert_not_called()
    
    @patch('services.analysis_orchestrator.RepoIngestionService')
    def test_clone_repository_success(self, mock_service_class, orchestrator):
        """Test successful repository cloning"""
        mock_service = mock_service_class.return_value
        mock_service.clone_repository.return_value = {
            'owner': 'owner',
            'name': 'repo',
            'local_path': '/path/to/repo',
            'branch': 'main'
        }
        
        orchestrator.ingestion_service = mock_service
        result = orchestrator._clone_repository(
            "https://github.com/owner/repo",
            "main",
            False
        )
        
        assert result['local_path'] == '/path/to/repo'
        mock_service.clone_repository.assert_called_once()
    
    @patch('services.analysis_orchestrator.TerraformParser')
    def test_parse_terraform_files(self, mock_parser_class, orchestrator, sample_parsed_repo):
        """Test Terraform file parsing"""
        mock_parser = mock_parser_class.return_value
        mock_parser.parse_repository.return_value = sample_parsed_repo
        
        orchestrator.parser = mock_parser
        result = orchestrator._parse_terraform_files("/path/to/repo")
        
        assert len(result.resources) == 1
        assert result.resources[0].type == "aws_vpc"
        mock_parser.parse_repository.assert_called_once_with("/path/to/repo")
    
    @patch('services.analysis_orchestrator.GraphBuilder')
    def test_build_graph(self, mock_builder_class, orchestrator, sample_parsed_repo, sample_graph_result):
        """Test graph building"""
        mock_builder = mock_builder_class.return_value
        mock_builder.build_graph.return_value = sample_graph_result
        
        orchestrator.graph_builder = mock_builder
        result = orchestrator._build_graph(sample_parsed_repo)
        
        assert result.statistics.total_nodes == 1
        assert result.statistics.total_resources == 1
        mock_builder.build_graph.assert_called_once()
    
    def test_store_terraform_files(self, orchestrator, mock_db, sample_parsed_repo):
        """Test storing Terraform files in database"""
        repo = Repository(id=1, name='test', url='https://github.com/test/test')
        
        orchestrator._store_terraform_files(repo, "/path/to/repo", sample_parsed_repo)
        
        # Verify delete was called
        mock_db.query.return_value.filter_by.return_value.delete.assert_called()
        # Verify add was called for each file
        assert mock_db.add.call_count >= len(sample_parsed_repo.files)
    
    def test_store_parsed_components(self, orchestrator, mock_db, sample_parsed_repo):
        """Test storing parsed components in database"""
        repo = Repository(id=1, name='test', url='https://github.com/test/test')
        
        # Mock first file query
        from models.models import TerraformFile
        mock_file = TerraformFile(id=1, repository_id=1, file_path="main.tf", content="")
        mock_db.query.return_value.filter_by.return_value.first.return_value = mock_file
        
        orchestrator._store_parsed_components(repo, sample_parsed_repo)
        
        # Verify components were added
        assert mock_db.add.call_count > 0
    
    def test_mark_failed(self, orchestrator, mock_db):
        """Test marking repository as failed"""
        repo = Repository(id=1, name='test', url='https://github.com/test/test', status='analyzing')
        error_msg = "Test error"
        
        orchestrator._mark_failed(repo, error_msg)
        
        assert repo.status == 'failed'
        assert repo.error_message == error_msg
        assert repo.analyzed_at is not None
        mock_db.commit.assert_called_once()
    
    def test_get_analysis_status_found(self, orchestrator, mock_db):
        """Test getting analysis status for existing repository"""
        repo = Repository(
            id=1,
            name='test',
            url='https://github.com/test/test',
            status='completed',
            total_resources=5,
            total_modules=2
        )
        mock_db.query.return_value.filter_by.return_value.first.return_value = repo
        
        status = orchestrator.get_analysis_status(1)
        
        assert status is not None
        assert status['id'] == 1
        assert status['status'] == 'completed'
        assert status['statistics']['total_resources'] == 5
    
    def test_get_analysis_status_not_found(self, orchestrator, mock_db):
        """Test getting analysis status for non-existent repository"""
        mock_db.query.return_value.filter_by.return_value.first.return_value = None
        
        status = orchestrator.get_analysis_status(999)
        
        assert status is None
    
    @patch.object(AnalysisOrchestrator, '_validate_url')
    @patch.object(AnalysisOrchestrator, '_get_or_create_repository')
    @patch.object(AnalysisOrchestrator, '_clone_repository')
    @patch.object(AnalysisOrchestrator, '_parse_terraform_files')
    @patch.object(AnalysisOrchestrator, '_build_graph')
    @patch.object(AnalysisOrchestrator, '_store_terraform_files')
    @patch.object(AnalysisOrchestrator, '_store_parsed_components')
    @patch.object(AnalysisOrchestrator, '_store_graph')
    @patch.object(AnalysisOrchestrator, '_generate_summary')
    @patch.object(AnalysisOrchestrator, '_update_statistics')
    def test_analyze_repository_success(
        self,
        mock_update_stats,
        mock_gen_summary,
        mock_store_graph,
        mock_store_components,
        mock_store_files,
        mock_build_graph,
        mock_parse,
        mock_clone,
        mock_get_repo,
        mock_validate,
        orchestrator,
        mock_db,
        sample_parsed_repo,
        sample_graph_result
    ):
        """Test complete successful analysis workflow"""
        # Setup mocks
        mock_validate.return_value = {'owner': 'owner', 'name': 'repo', 'url': 'https://github.com/owner/repo'}
        
        repo = Repository(id=1, name='repo', url='https://github.com/owner/repo', status='pending')
        mock_get_repo.return_value = repo
        
        mock_clone.return_value = {'local_path': '/path/to/repo'}
        mock_parse.return_value = sample_parsed_repo
        mock_build_graph.return_value = sample_graph_result
        
        # Execute
        result = orchestrator.analyze_repository("https://github.com/owner/repo")
        
        # Verify
        assert result.status == 'completed'
        assert result.analyzed_at is not None
        mock_validate.assert_called_once()
        mock_clone.assert_called_once()
        mock_parse.assert_called_once()
        mock_build_graph.assert_called_once()
        mock_store_files.assert_called_once()
        mock_store_components.assert_called_once()
        mock_store_graph.assert_called_once()
        mock_gen_summary.assert_called_once()
        mock_update_stats.assert_called_once()
    
    @patch.object(AnalysisOrchestrator, '_validate_url')
    def test_analyze_repository_validation_error(self, mock_validate, orchestrator):
        """Test analysis with validation error"""
        from services.repo_ingestion_service import RepositoryValidationError
        mock_validate.side_effect = RepositoryValidationError("Invalid URL")
        
        with pytest.raises(AnalysisError) as exc_info:
            orchestrator.analyze_repository("invalid-url")
        
        assert "URL validation failed" in str(exc_info.value)
    
    @patch.object(AnalysisOrchestrator, '_validate_url')
    @patch.object(AnalysisOrchestrator, '_get_or_create_repository')
    @patch.object(AnalysisOrchestrator, '_clone_repository')
    def test_analyze_repository_clone_error(
        self,
        mock_clone,
        mock_get_repo,
        mock_validate,
        orchestrator,
        mock_db
    ):
        """Test analysis with cloning error"""
        from services.repo_ingestion_service import RepositoryIngestionError
        
        mock_validate.return_value = {'owner': 'owner', 'name': 'repo', 'url': 'https://github.com/owner/repo'}
        repo = Repository(id=1, name='repo', url='https://github.com/owner/repo', status='pending')
        mock_get_repo.return_value = repo
        mock_clone.side_effect = RepositoryIngestionError("Clone failed")
        
        with pytest.raises(AnalysisError) as exc_info:
            orchestrator.analyze_repository("https://github.com/owner/repo")
        
        assert "Repository cloning failed" in str(exc_info.value)
        assert repo.status == 'failed'


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

# Made with Bob
