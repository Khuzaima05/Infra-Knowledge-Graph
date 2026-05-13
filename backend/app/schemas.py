"""
Pydantic schemas for API requests/responses
"""

from pydantic import BaseModel, HttpUrl
from typing import Optional, List, Dict, Any
from datetime import datetime


# Analysis Schemas
class AnalysisRequest(BaseModel):
    url: str
    branch: Optional[str] = "main"


class AnalysisResponse(BaseModel):
    id: int
    name: str

# Graph Search Schemas
class GraphSearchResult(BaseModel):
    """Graph node search result"""
    node_id: str
    label: str
    type: str
    data: Dict[str, Any]
    score: int
    metadata: Dict[str, Any] = {}

class GraphNodeResponse(BaseModel):
    """Detailed graph node response"""
    node: Dict[str, Any]
    outgoing_edges: List[Dict[str, Any]]
    incoming_edges: List[Dict[str, Any]]
    connected_nodes: List[Dict[str, Any]]
    dependency_count: Dict[str, int]

    url: str
    status: str
    total_resources: int
    total_modules: int
    total_variables: int
    providers_count: int
    
    class Config:
        from_attributes = True


# Repository Schemas
class RepositoryResponse(BaseModel):
    id: int
    name: str
    url: str
    branch: str
    status: str
    statistics: Dict[str, int]
    analyzed_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


# Graph Schemas
class GraphNodeData(BaseModel):
    id: str
    label: str
    type: str
    data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None


class GraphEdgeData(BaseModel):
    id: str
    source: str
    target: str
    type: str
    data: Dict[str, Any]


class GraphResponse(BaseModel):
    id: int
    repository_id: int
    nodes: List[GraphNodeData]
    edges: List[GraphEdgeData]
    statistics: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Summary Schemas
class SummaryResponse(BaseModel):
    id: int
    repository_id: int
    title: str
    architecture_description: str
    key_components: List[Dict[str, str]]
    deployment_overview: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


# Resource Schemas
class ResourceResponse(BaseModel):
    id: int
    type: str
    name: str
    full_name: str
    provider: Optional[str]
    metadata: Dict[str, Any]
    
    class Config:
        from_attributes = True


class VariableResponse(BaseModel):
    id: int
    name: str
    type: str
    default_value: Optional[str]
    description: str
    
    class Config:
        from_attributes = True


# Repository Ingestion Schemas
class RepoIngestionRequest(BaseModel):
    url: str
    branch: Optional[str] = "main"
    force_refresh: Optional[bool] = False


class RepoMetadataResponse(BaseModel):
    owner: str
    name: str
    url: str
    local_path: str
    branch: str
    commit_hash: Optional[str] = None
    commit_message: Optional[str] = None
    commit_author: Optional[str] = None
    commit_date: Optional[str] = None
    total_commits: Optional[int] = None
    is_cloned: bool


class TerraformFilesResponse(BaseModel):
    owner: str
    name: str
    terraform_files: List[str]
    total_files: int


class StorageUsageResponse(BaseModel):
    total_bytes: int
    total_mb: float
    repositories: int


class CleanupStatsResponse(BaseModel):
    checked: int
    deleted: int
    errors: int


class ModuleResponse(BaseModel):
    id: int
    name: str
    source: Optional[str]
    version: Optional[str]
    metadata: Dict[str, Any]
    
    class Config:
        from_attributes = True


# Analysis Workflow Schemas
class AnalysisStatusResponse(BaseModel):
    id: int
    name: str
    url: str
    status: str  # pending, analyzing, completed, failed
    analyzed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    statistics: Dict[str, int]


class AnalysisProgressResponse(BaseModel):
    repository_id: int
    status: str
    current_step: Optional[str] = None
    progress_percentage: Optional[int] = None
    message: Optional[str] = None


class CompleteAnalysisRequest(BaseModel):
    url: str
    branch: Optional[str] = "main"
    force_refresh: Optional[bool] = False
    async_mode: Optional[bool] = True  # Run in background


class CompleteAnalysisResponse(BaseModel):
    repository_id: int
    status: str
    message: str
    analysis_started: bool
    estimated_time_seconds: Optional[int] = None


# Dashboard Schemas
class DashboardResponse(BaseModel):
    id: int
    name: str
    url: str
    status: str
    statistics: Dict[str, int]
    analyzed_at: Optional[datetime] = None


class RepositoryDashboardResponse(BaseModel):
    id: int
    name: str
    url: str
    branch: str
    status: str
    statistics: Dict[str, int]
    graph_statistics: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any]


class GraphStatisticsResponse(BaseModel):
    id: int
    repository_id: int
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    statistics: Dict[str, Any]
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProviderResponse(BaseModel):
    id: int
    name: str
    version: Optional[str]
    alias: Optional[str]
    
    class Config:
        from_attributes = True

# Architecture Summary Schemas
class KeyComponent(BaseModel):
    """Key infrastructure component"""
    name: str
    description: str
    type: Optional[str] = None

class ArchitectureSummaryResponse(BaseModel):
    """Architecture summary response"""
    repository_id: int
    title: str
    architecture_description: str
    key_components: List[Dict[str, Any]]
    deployment_overview: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
