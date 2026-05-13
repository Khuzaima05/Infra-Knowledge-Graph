"""Graph schemas for dependency visualization

Pydantic models for graph nodes, edges, and output format.
"""

from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field


class GraphNode(BaseModel):
    """Graph node representing a Terraform component"""
    id: str = Field(..., description="Unique node identifier")
    label: str = Field(..., description="Display label")
    type: Literal["resource", "module", "variable", "output", "provider", "local", "data_source"] = Field(
        ..., description="Node type"
    )
    data: Dict[str, Any] = Field(default_factory=dict, description="Node-specific data")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")
    position: Optional[Dict[str, float]] = Field(None, description="Layout position (x, y)")


class GraphEdge(BaseModel):
    """Graph edge representing a dependency relationship"""
    id: str = Field(..., description="Unique edge identifier")
    source: str = Field(..., description="Source node ID")
    target: str = Field(..., description="Target node ID")
    type: Literal["depends_on", "uses", "references", "provides", "contains"] = Field(
        ..., description="Edge type"
    )
    data: Dict[str, Any] = Field(default_factory=dict, description="Edge-specific data")
    weight: float = Field(default=1.0, description="Edge weight for layout")


class GraphStatistics(BaseModel):
    """Graph statistics and metrics"""
    total_nodes: int = Field(default=0, description="Total number of nodes")
    total_edges: int = Field(default=0, description="Total number of edges")
    node_types: Dict[str, int] = Field(default_factory=dict, description="Count by node type")
    edge_types: Dict[str, int] = Field(default_factory=dict, description="Count by edge type")
    connected_components: int = Field(default=0, description="Number of connected components")
    has_cycles: bool = Field(default=False, description="Whether graph contains cycles")
    max_depth: int = Field(default=0, description="Maximum dependency depth")
    avg_degree: float = Field(default=0.0, description="Average node degree")


class DependencyGraph(BaseModel):
    """Complete dependency graph output"""
    nodes: List[GraphNode] = Field(default_factory=list, description="Graph nodes")
    edges: List[GraphEdge] = Field(default_factory=list, description="Graph edges")
    statistics: GraphStatistics = Field(default_factory=GraphStatistics, description="Graph statistics")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Graph metadata")
    
    def to_json_format(self) -> Dict[str, Any]:
        """Convert to JSON format for API response"""
        return {
            "nodes": [node.model_dump() for node in self.nodes],
            "edges": [edge.model_dump() for edge in self.edges],
            "statistics": self.statistics.model_dump(),
            "metadata": self.metadata
        }


class ReferenceResolution(BaseModel):
    """Resolved reference information"""
    reference_type: str = Field(..., description="Type of reference")
    source_id: str = Field(..., description="Source component ID")
    target_id: str = Field(..., description="Target component ID")
    resolved: bool = Field(default=False, description="Whether reference was resolved")
    context: Optional[str] = Field(None, description="Reference context")


class VariableLineage(BaseModel):
    """Variable usage lineage"""
    variable_id: str = Field(..., description="Variable identifier")
    variable_name: str = Field(..., description="Variable name")
    default_value: Optional[Any] = Field(None, description="Default value")
    used_by: List[str] = Field(default_factory=list, description="Components using this variable")
    usage_count: int = Field(default=0, description="Number of usages")
    lineage_depth: int = Field(default=0, description="Depth in dependency tree")


class ModuleRelationship(BaseModel):
    """Module relationship information"""
    module_id: str = Field(..., description="Module identifier")
    module_name: str = Field(..., description="Module name")
    source: str = Field(..., description="Module source")
    parent_module: Optional[str] = Field(None, description="Parent module if nested")
    child_modules: List[str] = Field(default_factory=list, description="Child modules")
    resources: List[str] = Field(default_factory=list, description="Resources in module")
    variables_used: List[str] = Field(default_factory=list, description="Variables used by module")
    outputs_provided: List[str] = Field(default_factory=list, description="Outputs provided by module")

# Made with Bob
