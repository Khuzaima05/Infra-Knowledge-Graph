"""Analysis Orchestration Service

Coordinates the complete repository analysis workflow:
1. Clone repository
2. Parse Terraform files
3. Resolve references
4. Build dependency graph
5. Store metadata in database
6. Return comprehensive analysis
"""

import asyncio
from typing import Dict, List, Any, Optional
from pathlib import Path
from sqlalchemy.orm import Session
from datetime import datetime

from services.repo_ingestion_service import (
    RepoIngestionService,
    RepositoryValidationError,
    RepositoryIngestionError
)
from parser.terraform_parser_v2 import TerraformParser
from parser.parser_schemas import ParsedRepository
from graph.graph_builder_v2 import GraphBuilder
from graph.graph_schemas import GraphResult
from services.summary_generator import SummaryGenerator
from models.models import (
    Repository, TerraformFile, Module, Resource,
    Variable, Output, Provider, Graph, Summary
)
from config.logger import logger


class AnalysisError(Exception):
    """Base exception for analysis errors"""
    pass


class AnalysisOrchestrator:
    """Orchestrates complete infrastructure analysis workflow"""
    
    def __init__(self, db: Session, workspace_dir: str = "./cloned_repos"):
        """
        Initialize the orchestrator
        
        Args:
            db: Database session
            workspace_dir: Directory for cloned repositories
        """
        self.db = db
        self.workspace_dir = workspace_dir
        self.ingestion_service = RepoIngestionService(workspace_dir)
        self.parser = TerraformParser()
        self.graph_builder = GraphBuilder()
        logger.info("Initialized AnalysisOrchestrator")
    
    async def analyze_repository_async(
        self,
        url: str,
        branch: str = "main",
        force_refresh: bool = False
    ) -> Repository:
        """
        Async wrapper for repository analysis
        
        Args:
            url: GitHub repository URL
            branch: Git branch to analyze
            force_refresh: Force re-clone if already exists
            
        Returns:
            Repository model with analysis results
            
        Raises:
            AnalysisError: If analysis fails at any step
        """
        # Run synchronous analysis in thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None,
            self.analyze_repository,
            url,
            branch,
            force_refresh
        )
    
    def analyze_repository(
        self,
        url: str,
        branch: str = "main",
        force_refresh: bool = False
    ) -> Repository:
        """
        Complete synchronous analysis pipeline
        
        Workflow:
        1. Validate and parse GitHub URL
        2. Create/update repository record
        3. Clone repository locally
        4. Parse all Terraform files
        5. Resolve references and build graph
        6. Store all metadata in database
        7. Generate summary
        
        Args:
            url: GitHub repository URL
            branch: Git branch to analyze
            force_refresh: Force re-clone if already exists
            
        Returns:
            Repository model with complete analysis
            
        Raises:
            AnalysisError: If any step fails
        """
        repo_record = None
        
        try:
            # Step 1: Validate URL
            logger.info(f"Step 1: Validating URL: {url}")
            repo_info = self._validate_url(url)
            
            # Step 2: Create/get repository record
            logger.info(f"Step 2: Creating repository record for {repo_info['name']}")
            repo_record = self._get_or_create_repository(url, branch, repo_info)
            repo_record.status = 'analyzing'
            self.db.commit()
            
            # Step 3: Clone repository
            logger.info(f"Step 3: Cloning repository {url}")
            clone_metadata = self._clone_repository(url, branch, force_refresh)
            repo_record.cloned_path = clone_metadata['local_path']
            self.db.commit()
            
            # Step 4: Parse Terraform files
            logger.info(f"Step 4: Parsing Terraform files from {clone_metadata['local_path']}")
            parsed_repo = self._parse_terraform_files(clone_metadata['local_path'])
            
            # Step 5: Build dependency graph
            logger.info(f"Step 5: Building dependency graph")
            graph_result = self._build_graph(parsed_repo)
            
            # Step 6: Store metadata in database
            logger.info(f"Step 6: Storing metadata in database")
            self._store_terraform_files(repo_record, clone_metadata['local_path'], parsed_repo)
            self._store_parsed_components(repo_record, parsed_repo)
            self._store_graph(repo_record, graph_result)
            
            # Step 7: Generate summary
            logger.info(f"Step 7: Generating summary")
            self._generate_summary(repo_record, parsed_repo, graph_result)
            
            # Update statistics
            self._update_statistics(repo_record)
            
            # Mark as completed
            repo_record.status = 'completed'
            repo_record.analyzed_at = datetime.utcnow()
            repo_record.error_message = None
            self.db.commit()
            
            logger.info(f"Analysis completed successfully for repository {repo_record.id}")
            return repo_record
        
        except RepositoryValidationError as e:
            error_msg = f"URL validation failed: {str(e)}"
            logger.error(error_msg)
            if repo_record:
                self._mark_failed(repo_record, error_msg)
            raise AnalysisError(error_msg) from e
        
        except RepositoryIngestionError as e:
            error_msg = f"Repository cloning failed: {str(e)}"
            logger.error(error_msg)
            if repo_record:
                self._mark_failed(repo_record, error_msg)
            raise AnalysisError(error_msg) from e
        
        except Exception as e:
            error_msg = f"Analysis failed: {str(e)}"
            logger.exception(error_msg)
            if repo_record:
                self._mark_failed(repo_record, error_msg)
            raise AnalysisError(error_msg) from e
    
    def _validate_url(self, url: str) -> Dict[str, str]:
        """Validate and parse GitHub URL"""
        try:
            return self.ingestion_service.parse_github_url(url)
        except RepositoryValidationError:
            raise
    
    def _get_or_create_repository(
        self,
        url: str,
        branch: str,
        repo_info: Dict[str, str]
    ) -> Repository:
        """Get existing or create new repository record"""
        repo = self.db.query(Repository).filter_by(url=url).first()
        
        if repo:
            logger.info(f"Found existing repository record: {repo.id}")
            repo.branch = branch
            repo.updated_at = datetime.utcnow()
        else:
            logger.info(f"Creating new repository record for {repo_info['name']}")
            repo = Repository(
                name=repo_info['name'],
                url=url,
                branch=branch,
                status='pending'
            )
            self.db.add(repo)
            self.db.flush()
        
        return repo
    
    def _clone_repository(
        self,
        url: str,
        branch: str,
        force_refresh: bool
    ) -> Dict[str, Any]:
        """Clone repository using ingestion service"""
        try:
            return self.ingestion_service.clone_repository(
                url=url,
                branch=branch,
                force_refresh=force_refresh
            )
        except (RepositoryValidationError, RepositoryIngestionError):
            raise
    
    def _parse_terraform_files(self, repo_path: str) -> ParsedRepository:
        """Parse all Terraform files in repository"""
        try:
            return self.parser.parse_repository(repo_path)
        except Exception as e:
            raise AnalysisError(f"Terraform parsing failed: {str(e)}") from e
    
    def _build_graph(self, parsed_repo: ParsedRepository) -> GraphResult:
        """Build dependency graph from parsed components"""
        try:
            return self.graph_builder.build_graph(parsed_repo)
        except Exception as e:
            raise AnalysisError(f"Graph building failed: {str(e)}") from e
    
    def _store_terraform_files(
        self,
        repo: Repository,
        repo_path: str,
        parsed_repo: ParsedRepository
    ) -> None:
        """Store Terraform file records in database"""
        try:
            # Delete existing files for this repository
            self.db.query(TerraformFile).filter_by(repository_id=repo.id).delete()
            
            # Store each parsed file
            for file_data in parsed_repo.files:
                tf_file = TerraformFile(
                    repository_id=repo.id,
                    file_path=file_data.path,
                    content=file_data.content
                )
                self.db.add(tf_file)
            
            self.db.flush()
            logger.info(f"Stored {len(parsed_repo.files)} Terraform files")
        
        except Exception as e:
            raise AnalysisError(f"Failed to store Terraform files: {str(e)}") from e
    
    def _store_parsed_components(
        self,
        repo: Repository,
        parsed_repo: ParsedRepository
    ) -> None:
        """Store all parsed components in database"""
        try:
            # Get first file for associations (simplified approach)
            first_file = self.db.query(TerraformFile).filter_by(
                repository_id=repo.id
            ).first()
            
            if not first_file:
                logger.warning("No Terraform files found, skipping component storage")
                return
            
            # Delete existing components
            self.db.query(Module).filter_by(repository_id=repo.id).delete()
            self.db.query(Resource).filter_by(repository_id=repo.id).delete()
            self.db.query(Variable).filter_by(repository_id=repo.id).delete()
            self.db.query(Output).filter_by(repository_id=repo.id).delete()
            self.db.query(Provider).filter_by(repository_id=repo.id).delete()
            
            # Store modules
            for module in parsed_repo.modules:
                db_module = Module(
                    terraform_file_id=first_file.id,
                    repository_id=repo.id,
                    name=module.name,
                    source=module.source,
                    version=module.version,
                    metadata={
                        'inputs': module.inputs,
                        'file_path': module.file_path
                    }
                )
                self.db.add(db_module)
            
            # Store resources
            for resource in parsed_repo.resources:
                db_resource = Resource(
                    terraform_file_id=first_file.id,
                    repository_id=repo.id,
                    type=resource.type,
                    name=resource.name,
                    full_name=f"{resource.type}.{resource.name}",
                    provider=resource.provider,
                    metadata={
                        'attributes': resource.attributes,
                        'depends_on': resource.depends_on,
                        'file_path': resource.file_path
                    }
                )
                self.db.add(db_resource)
            
            # Store variables
            for variable in parsed_repo.variables:
                db_variable = Variable(
                    terraform_file_id=first_file.id,
                    repository_id=repo.id,
                    name=variable.name,
                    type=variable.type or 'string',
                    default_value=str(variable.default) if variable.default else None,
                    description=variable.description or '',
                    metadata={
                        'sensitive': variable.sensitive,
                        'file_path': variable.file_path
                    }
                )
                self.db.add(db_variable)
            
            # Store outputs
            for output in parsed_repo.outputs:
                db_output = Output(
                    terraform_file_id=first_file.id,
                    repository_id=repo.id,
                    name=output.name,
                    value=str(output.value) if output.value else None,
                    description=output.description or '',
                    metadata={
                        'sensitive': output.sensitive,
                        'file_path': output.file_path
                    }
                )
                self.db.add(db_output)
            
            # Store providers
            for provider in parsed_repo.providers:
                # Check for duplicates
                existing = self.db.query(Provider).filter_by(
                    repository_id=repo.id,
                    name=provider.name,
                    alias=provider.alias
                ).first()
                
                if not existing:
                    db_provider = Provider(
                        terraform_file_id=first_file.id,
                        repository_id=repo.id,
                        name=provider.name,
                        version=provider.version,
                        alias=provider.alias,
                        metadata={
                            'configuration': provider.configuration,
                            'file_path': provider.file_path
                        }
                    )
                    self.db.add(db_provider)
            
            self.db.flush()
            logger.info(
                f"Stored components: {len(parsed_repo.modules)} modules, "
                f"{len(parsed_repo.resources)} resources, "
                f"{len(parsed_repo.variables)} variables, "
                f"{len(parsed_repo.outputs)} outputs, "
                f"{len(parsed_repo.providers)} providers"
            )
        
        except Exception as e:
            raise AnalysisError(f"Failed to store parsed components: {str(e)}") from e
    
    def _store_graph(self, repo: Repository, graph_result: GraphResult) -> None:
        """Store dependency graph in database"""
        try:
            # Delete existing graph
            self.db.query(Graph).filter_by(repository_id=repo.id).delete()
            
            # Convert graph nodes and edges to JSON-serializable format
            nodes_data = [
                {
                    'id': node.id,
                    'type': node.type,
                    'label': node.label,
                    'data': node.data,
                    'metadata': node.metadata
                }
                for node in graph_result.nodes
            ]
            
            edges_data = [
                {
                    'id': edge.id,
                    'source': edge.source,
                    'target': edge.target,
                    'type': edge.type,
                    'label': edge.label,
                    'metadata': edge.metadata
                }
                for edge in graph_result.edges
            ]
            
            # Create graph record
            db_graph = Graph(
                repository_id=repo.id,
                nodes=nodes_data,
                edges=edges_data,
                node_count=graph_result.statistics.total_nodes,
                edge_count=graph_result.statistics.total_edges
            )
            self.db.add(db_graph)
            self.db.flush()
            
            logger.info(
                f"Stored graph: {graph_result.statistics.total_nodes} nodes, "
                f"{graph_result.statistics.total_edges} edges"
            )
        
        except Exception as e:
            raise AnalysisError(f"Failed to store graph: {str(e)}") from e
    
    def _generate_summary(
        self,
        repo: Repository,
        parsed_repo: ParsedRepository,
        graph_result: GraphResult
    ) -> None:
        """Generate and store architecture summary"""
        try:
            # Delete existing summary
            self.db.query(Summary).filter_by(repository_id=repo.id).delete()
            
            # Build summary
            title = f"{repo.name} Infrastructure Analysis"
            
            # Architecture description
            stats = graph_result.statistics
            architecture_description = (
                f"This Terraform infrastructure consists of {stats.total_resources} resources, "
                f"{stats.total_modules} modules, {stats.total_variables} variables, "
                f"and {stats.total_outputs} outputs across {stats.total_providers} provider(s). "
                f"The dependency graph contains {stats.total_nodes} nodes and {stats.total_edges} edges."
            )
            
            # Key components
            key_components = []
            
            # Add providers
            for provider in parsed_repo.providers[:5]:
                key_components.append({
                    'name': f"{provider.name} Provider" + (f" ({provider.alias})" if provider.alias else ""),
                    'description': f"Version: {provider.version or 'latest'}"
                })
            
            # Add top modules
            for module in parsed_repo.modules[:5]:
                key_components.append({
                    'name': f"Module: {module.name}",
                    'description': f"Source: {module.source or 'local'}"
                })
            
            # Deployment overview
            deployment_overview = (
                f"The infrastructure uses {stats.total_providers} cloud provider(s) "
                f"and defines {stats.total_resources} resources. "
                f"There are {stats.total_modules} reusable modules for modular infrastructure management. "
                f"The graph analysis identified {stats.total_edges} dependencies between components."
            )
            
            # Create summary record
            db_summary = Summary(
                repository_id=repo.id,
                title=title,
                architecture_description=architecture_description,
                key_components=key_components,
                deployment_overview=deployment_overview
            )
            self.db.add(db_summary)
            self.db.flush()
            
            logger.info("Generated and stored summary")
        
        except Exception as e:
            raise AnalysisError(f"Failed to generate summary: {str(e)}") from e
    
    def _update_statistics(self, repo: Repository) -> None:
        """Update repository statistics"""
        try:
            repo.total_modules = self.db.query(Module).filter_by(
                repository_id=repo.id
            ).count()
            repo.total_resources = self.db.query(Resource).filter_by(
                repository_id=repo.id
            ).count()
            repo.total_variables = self.db.query(Variable).filter_by(
                repository_id=repo.id
            ).count()
            repo.total_outputs = self.db.query(Output).filter_by(
                repository_id=repo.id
            ).count()
            repo.providers_count = self.db.query(Provider).filter_by(
                repository_id=repo.id
            ).count()
            
            logger.info(f"Updated statistics for repository {repo.id}")
        
        except Exception as e:
            logger.error(f"Failed to update statistics: {str(e)}")
    
    def _mark_failed(self, repo: Repository, error_message: str) -> None:
        """Mark repository analysis as failed"""
        try:
            repo.status = 'failed'
            repo.error_message = error_message
            repo.analyzed_at = datetime.utcnow()
            self.db.commit()
        except Exception as e:
            logger.error(f"Failed to mark repository as failed: {str(e)}")
            self.db.rollback()
    
    def get_analysis_status(self, repo_id: int) -> Optional[Dict[str, Any]]:
        """
        Get current analysis status for a repository
        
        Args:
            repo_id: Repository ID
            
        Returns:
            Dictionary with status information or None if not found
        """
        repo = self.db.query(Repository).filter_by(id=repo_id).first()
        
        if not repo:
            return None
        
        return {
            'id': repo.id,
            'name': repo.name,
            'url': repo.url,
            'status': repo.status,
            'analyzed_at': repo.analyzed_at,
            'error_message': repo.error_message,
            'statistics': {
                'total_resources': repo.total_resources,
                'total_modules': repo.total_modules,
                'total_variables': repo.total_variables,
                'total_outputs': repo.total_outputs,
                'providers_count': repo.providers_count
            }
        }

# Made with Bob
