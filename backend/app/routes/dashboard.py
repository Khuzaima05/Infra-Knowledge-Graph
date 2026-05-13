"""Dashboard API Routes

Comprehensive dashboard endpoints for repository statistics and metadata.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List, Optional

from models.database import get_db
from models.models import (
    Repository, Graph, Summary, Module, Resource,
    Variable, Output, Provider, TerraformFile
)
from app.schemas import (
    DashboardResponse,
    RepositoryDashboardResponse,
    GraphStatisticsResponse,
    SummaryResponse
)
from config.logger import logger

router = APIRouter()


@router.get("/repo/{repo_id}", response_model=RepositoryDashboardResponse)
def get_repository_dashboard(repo_id: int, db: Session = Depends(get_db)):
    """
    Get comprehensive repository dashboard with all statistics
    
    **Returns:**
    - Repository metadata (name, URL, branch, status)
    - Resource counts (resources, modules, variables, outputs, providers)
    - Dependency counts (total edges in graph)
    - Graph statistics (nodes, edges, complexity metrics)
    - File information
    - Timestamps
    
    **Example Response:**
    ```json
    {
        "id": 1,
        "name": "terraform-aws-vpc",
        "url": "https://github.com/terraform-aws-modules/terraform-aws-vpc",
        "branch": "main",
        "status": "completed",
        "statistics": {
            "resources": 45,
            "modules": 3,
            "variables": 12,
            "outputs": 8,
            "providers": 1,
            "files": 15,
            "dependencies": 67
        },
        "graph_statistics": {
            "total_nodes": 69,
            "total_edges": 67,
            "resource_nodes": 45,
            "module_nodes": 3,
            "variable_nodes": 12,
            "output_nodes": 8,
            "provider_nodes": 1
        },
        "metadata": {
            "analyzed_at": "2024-01-15T10:30:00Z",
            "created_at": "2024-01-15T10:25:00Z",
            "updated_at": "2024-01-15T10:30:00Z",
            "cloned_path": "/path/to/repo"
        }
    }
    ```
    """
    try:
        # Get repository
        repo = db.query(Repository).filter_by(id=repo_id).first()
        if not repo:
            raise HTTPException(
                status_code=404,
                detail=f"Repository {repo_id} not found"
            )
        
        # Get graph for dependency count
        graph = db.query(Graph).filter_by(repository_id=repo_id).first()
        dependency_count = graph.edge_count if graph else 0
        
        # Get file count
        file_count = db.query(TerraformFile).filter_by(
            repository_id=repo_id
        ).count()
        
        # Build graph statistics
        graph_stats = None
        if graph:
            # Count nodes by type
            nodes = graph.nodes or []
            node_types = {}
            for node in nodes:
                node_type = node.get('type', 'unknown')
                node_types[node_type] = node_types.get(node_type, 0) + 1
            
            graph_stats = {
                "total_nodes": graph.node_count,
                "total_edges": graph.edge_count,
                "resource_nodes": node_types.get('resource', 0),
                "module_nodes": node_types.get('module', 0),
                "variable_nodes": node_types.get('variable', 0),
                "output_nodes": node_types.get('output', 0),
                "provider_nodes": node_types.get('provider', 0),
                "data_source_nodes": node_types.get('data', 0),
                "local_nodes": node_types.get('local', 0)
            }
        
        # Build response
        return RepositoryDashboardResponse(
            id=repo.id,
            name=repo.name,
            url=repo.url,
            branch=repo.branch,
            status=repo.status,
            statistics={
                "resources": repo.total_resources,
                "modules": repo.total_modules,
                "variables": repo.total_variables,
                "outputs": repo.total_outputs,
                "providers": repo.providers_count,
                "files": file_count,
                "dependencies": dependency_count
            },
            graph_statistics=graph_stats,
            metadata={
                "analyzed_at": repo.analyzed_at,
                "created_at": repo.created_at,
                "updated_at": repo.updated_at,
                "cloned_path": repo.cloned_path,
                "error_message": repo.error_message
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error getting repository dashboard: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get repository dashboard: {str(e)}"
        )


@router.get("/summary/{repo_id}", response_model=SummaryResponse)
def get_repository_summary(repo_id: int, db: Session = Depends(get_db)):
    """
    Get architecture summary for repository
    
    **Returns:**
    - Title and description
    - Key components list
    - Deployment overview
    - Timestamps
    
    **Example Response:**
    ```json
    {
        "id": 1,
        "repository_id": 1,
        "title": "terraform-aws-vpc Infrastructure Analysis",
        "architecture_description": "This Terraform infrastructure consists of...",
        "key_components": [
            {
                "name": "aws Provider",
                "description": "Version: ~> 5.0"
            }
        ],
        "deployment_overview": "The infrastructure uses 1 cloud provider(s)...",
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z"
    }
    ```
    """
    try:
        # Verify repository exists
        repo = db.query(Repository).filter_by(id=repo_id).first()
        if not repo:
            raise HTTPException(
                status_code=404,
                detail=f"Repository {repo_id} not found"
            )
        
        # Get summary
        summary = db.query(Summary).filter_by(repository_id=repo_id).first()
        if not summary:
            raise HTTPException(
                status_code=404,
                detail=f"Summary not found for repository {repo_id}"
            )
        
        return SummaryResponse(
            id=summary.id,
            repository_id=summary.repository_id,
            title=summary.title,
            architecture_description=summary.architecture_description,
            key_components=summary.key_components,
            deployment_overview=summary.deployment_overview,
            created_at=summary.created_at,
            updated_at=summary.updated_at
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error getting repository summary: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get repository summary: {str(e)}"
        )


@router.get("/graph/{repo_id}", response_model=GraphStatisticsResponse)
def get_graph_statistics(repo_id: int, db: Session = Depends(get_db)):
    """
    Get detailed graph statistics and structure
    
    **Returns:**
    - Complete graph with nodes and edges
    - Detailed statistics by node type
    - Edge type breakdown
    - Complexity metrics
    
    **Example Response:**
    ```json
    {
        "id": 1,
        "repository_id": 1,
        "nodes": [...],
        "edges": [...],
        "statistics": {
            "total_nodes": 69,
            "total_edges": 67,
            "node_types": {
                "resource": 45,
                "module": 3,
                "variable": 12
            },
            "edge_types": {
                "depends_on": 30,
                "uses": 25,
                "references": 12
            },
            "complexity_metrics": {
                "average_degree": 1.94,
                "max_degree": 8,
                "density": 0.028
            }
        },
        "created_at": "2024-01-15T10:30:00Z",
        "updated_at": "2024-01-15T10:30:00Z"
    }
    ```
    """
    try:
        # Verify repository exists
        repo = db.query(Repository).filter_by(id=repo_id).first()
        if not repo:
            raise HTTPException(
                status_code=404,
                detail=f"Repository {repo_id} not found"
            )
        
        # Get graph
        graph = db.query(Graph).filter_by(repository_id=repo_id).first()
        if not graph:
            raise HTTPException(
                status_code=404,
                detail=f"Graph not found for repository {repo_id}"
            )
        
        # Analyze nodes
        nodes = graph.nodes or []
        node_types = {}
        for node in nodes:
            node_type = node.get('type', 'unknown')
            node_types[node_type] = node_types.get(node_type, 0) + 1
        
        # Analyze edges
        edges = graph.edges or []
        edge_types = {}
        for edge in edges:
            edge_type = edge.get('type', 'unknown')
            edge_types[edge_type] = edge_types.get(edge_type, 0) + 1
        
        # Calculate complexity metrics
        total_nodes = len(nodes)
        total_edges = len(edges)
        
        # Average degree (edges per node)
        avg_degree = (2 * total_edges / total_nodes) if total_nodes > 0 else 0
        
        # Calculate max degree (most connected node)
        node_degrees = {}
        for edge in edges:
            source = edge.get('source')
            target = edge.get('target')
            if source:
                node_degrees[source] = node_degrees.get(source, 0) + 1
            if target:
                node_degrees[target] = node_degrees.get(target, 0) + 1
        
        max_degree = max(node_degrees.values()) if node_degrees else 0
        
        # Graph density (actual edges / possible edges)
        max_possible_edges = total_nodes * (total_nodes - 1) / 2
        density = (total_edges / max_possible_edges) if max_possible_edges > 0 else 0
        
        return GraphStatisticsResponse(
            id=graph.id,
            repository_id=graph.repository_id,
            nodes=nodes,
            edges=edges,
            statistics={
                "total_nodes": total_nodes,
                "total_edges": total_edges,
                "node_types": node_types,
                "edge_types": edge_types,
                "complexity_metrics": {
                    "average_degree": round(avg_degree, 2),
                    "max_degree": max_degree,
                    "density": round(density, 4)
                }
            },
            created_at=graph.created_at,
            updated_at=graph.updated_at
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.exception(f"Error getting graph statistics: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get graph statistics: {str(e)}"
        )


@router.get("/overview", response_model=List[DashboardResponse])
def get_all_repositories_overview(
    skip: int = 0,
    limit: int = 10,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    Get overview of all repositories with key statistics
    
    **Query Parameters:**
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum records to return (default: 10, max: 100)
    - **status**: Filter by status (pending, analyzing, completed, failed)
    
    **Returns:**
    List of repositories with:
    - Basic metadata
    - Key statistics
    - Status information
    
    **Example Response:**
    ```json
    [
        {
            "id": 1,
            "name": "terraform-aws-vpc",
            "url": "https://github.com/terraform-aws-modules/terraform-aws-vpc",
            "status": "completed",
            "statistics": {
                "resources": 45,
                "modules": 3,
                "dependencies": 67
            },
            "analyzed_at": "2024-01-15T10:30:00Z"
        }
    ]
    ```
    """
    try:
        # Validate limit
        if limit > 100:
            limit = 100
        
        # Build query
        query = db.query(Repository)
        
        if status:
            query = query.filter_by(status=status)
        
        # Get repositories
        repos = query.offset(skip).limit(limit).all()
        
        # Build response for each repository
        result = []
        for repo in repos:
            # Get graph for dependency count
            graph = db.query(Graph).filter_by(repository_id=repo.id).first()
            dependency_count = graph.edge_count if graph else 0
            
            result.append(DashboardResponse(
                id=repo.id,
                name=repo.name,
                url=repo.url,
                status=repo.status,
                statistics={
                    "resources": repo.total_resources,
                    "modules": repo.total_modules,
                    "variables": repo.total_variables,
                    "outputs": repo.total_outputs,
                    "providers": repo.providers_count,
                    "dependencies": dependency_count
                },
                analyzed_at=repo.analyzed_at
            ))
        
        return result
    
    except Exception as e:
        logger.exception(f"Error getting repositories overview: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get repositories overview: {str(e)}"
        )

# Made with Bob
