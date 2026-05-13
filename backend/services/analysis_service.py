from typing import Dict, List, Any
from sqlalchemy.orm import Session
from parser.terraform_parser import TerraformParser
from parser.repository_manager import RepositoryManager
from graph.graph_builder import GraphBuilder, DependencyAnalyzer
from models.models import (
    Repository, TerraformFile, Module, Resource, 
    Variable, Output, Provider, Relationship, Graph, Summary
)
from datetime import datetime
import os


class AnalysisService:
    """Orchestrate complete infrastructure analysis workflow"""
    
    def __init__(self, db: Session, workspace_dir: str = "./cloned_repos"):
        self.db = db
        self.parser = TerraformParser(workspace_dir)
        self.repo_manager = RepositoryManager(workspace_dir)
    
    def analyze_repository(
        self,
        url: str,
        branch: str = "main"
    ) -> Repository:
        """
        Complete analysis pipeline:
        1. Clone repository
        2. Parse Terraform files
        3. Extract components
        4. Detect dependencies
        5. Generate graph
        6. Create summary
        """
        repo_info = self.repo_manager.extract_repo_info(url)
        repo_name = repo_info['name']
        
        # Create or get repository record
        db_repo = self.db.query(Repository).filter_by(url=url).first()
        if not db_repo:
            db_repo = Repository(
                name=repo_name,
                url=url,
                branch=branch,
                status='pending'
            )
            self.db.add(db_repo)
            self.db.flush()
        
        db_repo.status = 'analyzing'
        
        try:
            # Clone repository
            local_path = self.repo_manager.clone_repository(url, branch)
            db_repo.cloned_path = local_path
            
            # Parse Terraform files
            parse_result = self.parser.parse_repository(local_path)
            
            # Extract all files
            self._save_terraform_files(db_repo, local_path)
            
            # Save parsed components
            self._save_modules(db_repo, parse_result.get('modules', []))
            self._save_resources(db_repo, parse_result.get('resources', []))
            self._save_variables(db_repo, parse_result.get('variables', []))
            self._save_outputs(db_repo, parse_result.get('outputs', []))
            self._save_providers(db_repo, parse_result.get('providers', []))
            
            # Build graph and save relationships
            graph_data = self._build_and_save_graph(db_repo, parse_result)
            
            # Generate summary
            self._generate_summary(db_repo, parse_result)
            
            # Update statistics
            db_repo.total_modules = self.db.query(Module).filter_by(repository_id=db_repo.id).count()
            db_repo.total_resources = self.db.query(Resource).filter_by(repository_id=db_repo.id).count()
            db_repo.total_variables = self.db.query(Variable).filter_by(repository_id=db_repo.id).count()
            db_repo.total_outputs = self.db.query(Output).filter_by(repository_id=db_repo.id).count()
            db_repo.providers_count = self.db.query(Provider).filter_by(repository_id=db_repo.id).count()
            
            db_repo.status = 'completed'
            db_repo.analyzed_at = datetime.utcnow()
            
            self.db.commit()
        
        except Exception as e:
            db_repo.status = 'failed'
            db_repo.error_message = str(e)
            self.db.commit()
            raise
        
        return db_repo
    
    def _save_terraform_files(self, repo: Repository, repo_path: str) -> None:
        """Save all Terraform files found in repository"""
        tf_files = self.parser.find_terraform_files(repo_path)
        
        for file_path in tf_files:
            rel_path = os.path.relpath(file_path, repo_path)
            
            with open(file_path, 'r') as f:
                content = f.read()
            
            tf_file = TerraformFile(
                repository_id=repo.id,
                file_path=rel_path,
                content=content
            )
            self.db.add(tf_file)
        
        self.db.flush()
    
    def _save_modules(self, repo: Repository, modules: List[Dict[str, Any]]) -> None:
        """Save modules to database"""
        # Get first Terraform file (for simplicity, modules are associated with first file)
        first_file = self.db.query(TerraformFile).filter_by(repository_id=repo.id).first()
        
        if not first_file:
            return
        
        for module in modules:
            db_module = Module(
                terraform_file_id=first_file.id,
                repository_id=repo.id,
                name=module['name'],
                source=module.get('source'),
                version=module.get('version'),
                metadata=module.get('metadata', {})
            )
            self.db.add(db_module)
        
        self.db.flush()
    
    def _save_resources(self, repo: Repository, resources: List[Dict[str, Any]]) -> None:
        """Save resources to database"""
        first_file = self.db.query(TerraformFile).filter_by(repository_id=repo.id).first()
        
        if not first_file:
            return
        
        for resource in resources:
            db_resource = Resource(
                terraform_file_id=first_file.id,
                repository_id=repo.id,
                type=resource['type'],
                name=resource['name'],
                full_name=resource['full_name'],
                provider=resource.get('provider'),
                metadata=resource.get('metadata', {})
            )
            self.db.add(db_resource)
        
        self.db.flush()
    
    def _save_variables(self, repo: Repository, variables: List[Dict[str, Any]]) -> None:
        """Save variables to database"""
        first_file = self.db.query(TerraformFile).filter_by(repository_id=repo.id).first()
        
        if not first_file:
            return
        
        for variable in variables:
            db_var = Variable(
                terraform_file_id=first_file.id,
                repository_id=repo.id,
                name=variable['name'],
                type=variable.get('type', 'string'),
                default_value=variable.get('default_value'),
                description=variable.get('description', ''),
                metadata=variable.get('metadata', {})
            )
            self.db.add(db_var)
        
        self.db.flush()
    
    def _save_outputs(self, repo: Repository, outputs: List[Dict[str, Any]]) -> None:
        """Save outputs to database"""
        first_file = self.db.query(TerraformFile).filter_by(repository_id=repo.id).first()
        
        if not first_file:
            return
        
        for output in outputs:
            db_output = Output(
                terraform_file_id=first_file.id,
                repository_id=repo.id,
                name=output['name'],
                value=output.get('value'),
                description=output.get('description', ''),
                metadata=output.get('metadata', {})
            )
            self.db.add(db_output)
        
        self.db.flush()
    
    def _save_providers(self, repo: Repository, providers: List[Dict[str, Any]]) -> None:
        """Save providers to database"""
        first_file = self.db.query(TerraformFile).filter_by(repository_id=repo.id).first()
        
        if not first_file:
            return
        
        for provider in providers:
            # Skip duplicates
            existing = self.db.query(Provider).filter_by(
                repository_id=repo.id,
                name=provider['name']
            ).first()
            
            if not existing:
                db_provider = Provider(
                    terraform_file_id=first_file.id,
                    repository_id=repo.id,
                    name=provider['name'],
                    version=provider.get('version'),
                    alias=provider.get('alias'),
                    metadata=provider.get('metadata', {})
                )
                self.db.add(db_provider)
        
        self.db.flush()
    
    def _build_and_save_graph(
        self,
        repo: Repository,
        parse_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Build dependency graph and save to database"""
        builder = GraphBuilder()
        
        # Get file content for reference detection
        first_file = self.db.query(TerraformFile).filter_by(repository_id=repo.id).first()
        file_content = first_file.content if first_file else ""
        
        graph_data = builder.build_graph(
            modules=parse_result.get('modules', []),
            resources=parse_result.get('resources', []),
            variables=parse_result.get('variables', []),
            outputs=parse_result.get('outputs', []),
            providers=parse_result.get('providers', []),
            references=parse_result.get('references', []),
            file_content=file_content
        )
        
        # Save graph
        db_graph = Graph(
            repository_id=repo.id,
            nodes=graph_data['nodes'],
            edges=graph_data['edges'],
            node_count=graph_data['nodeCount'],
            edge_count=graph_data['edgeCount']
        )
        self.db.add(db_graph)
        
        return graph_data
    
    def _generate_summary(
        self,
        repo: Repository,
        parse_result: Dict[str, Any]
    ) -> None:
        """Generate architecture summary"""
        title = f"{repo.name} Infrastructure"
        
        # Build simple summary using templates
        components = parse_result.get('resources', [])
        providers = parse_result.get('providers', [])
        modules = parse_result.get('modules', [])
        
        key_components = []
        
        # Add providers
        for provider in providers:
            key_components.append({
                'name': f"{provider['name']} Provider",
                'description': f"Manages resources on {provider['name'].upper()}"
            })
        
        # Add modules
        for module in modules[:5]:  # Limit to 5
            key_components.append({
                'name': f"Module: {module['name']}",
                'description': f"Sourced from {module.get('source', 'local')}"
            })
        
        # Build description
        resource_count = len(components)
        provider_count = len(providers)
        module_count = len(modules)
        
        architecture_description = (
            f"This Terraform infrastructure defines {resource_count} resources "
            f"across {provider_count} provider(s). The setup includes {module_count} reusable module(s) "
            f"for modular infrastructure management."
        )
        
        deployment_overview = (
            f"The infrastructure consists of {provider_count} cloud provider(s) "
            f"{'and ' + str(module_count) + ' external module(s) ' if module_count > 0 else ''}. "
            f"Total resources to be deployed: {resource_count}."
        )
        
        db_summary = Summary(
            repository_id=repo.id,
            title=title,
            architecture_description=architecture_description,
            key_components=key_components,
            deployment_overview=deployment_overview
        )
        self.db.add(db_summary)


class RepositoryService:
    """Service for repository management operations"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_repository(self, repo_id: int) -> Repository:
        """Get repository by ID"""
        return self.db.query(Repository).filter_by(id=repo_id).first()
    
    def list_repositories(self, skip: int = 0, limit: int = 10) -> List[Repository]:
        """List all repositories with pagination"""
        return self.db.query(Repository).offset(skip).limit(limit).all()
    
    def get_repository_graph(self, repo_id: int) -> Graph:
        """Get graph for repository"""
        return self.db.query(Graph).filter_by(repository_id=repo_id).first()
    
    def get_repository_summary(self, repo_id: int) -> Summary:
        """Get summary for repository"""
        return self.db.query(Summary).filter_by(repository_id=repo_id).first()
