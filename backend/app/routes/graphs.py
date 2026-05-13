"""Graph API Routes

Endpoints for graph data retrieval and search functionality.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any

from models.database import get_db
from models.models import Repository, Graph
from app.schemas import GraphSearchResult, GraphNodeResponse
from config.logger import logger

router = APIRouter()


@router.get("/{repo_id}/dependency-graph")
def get_dependency_graph(repo_id: int, db: Session = Depends(get_db)):
    """
    Get complete dependency graph for a repository
    
    **Parameters:**
    - **repo_id**: Repository ID
    
    **Returns:**
    - Complete graph with nodes and edges
    - Node and edge counts
    - Graph metadata
    
    **Raises:**
    - 404: Repository or graph not found
    """
    logger.info(f"Fetching dependency graph for repository {repo_id}")
    
    # Check repository exists
    repo = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail=f"Repository {repo_id} not found")
    
    # Get graph
    graph = db.query(Graph).filter(Graph.repository_id == repo_id).first()
    if not graph:
        raise HTTPException(
            status_code=404,
            detail=f"Graph not found for repository {repo_id}. Run analysis first."
        )
    
    logger.info(f"Retrieved graph: {graph.node_count} nodes, {graph.edge_count} edges")
    
    return {
        "repository_id": repo_id,
        "nodes": graph.nodes,
        "edges": graph.edges,
        "node_count": graph.node_count,
        "edge_count": graph.edge_count,
        "graph_type": graph.graph_type,
        "created_at": graph.created_at,
        "updated_at": graph.updated_at
    }


@router.get("/{repo_id}/search", response_model=List[GraphSearchResult])
def search_graph_nodes(
    repo_id: int,
    query: str = Query(..., min_length=1, description="Search query"),
    node_type: Optional[str] = Query(None, description="Filter by node type"),
    limit: int = Query(50, ge=1, le=100, description="Maximum results"),
    db: Session = Depends(get_db)
):
    """
    Search graph nodes by name or ID
    
    **Parameters:**
    - **repo_id**: Repository ID
    - **query**: Search term (minimum 1 character)
    - **node_type**: Optional filter by node type (resource, module, variable, output, provider)
    - **limit**: Maximum number of results (1-100, default 50)
    
    **Returns:**
    - List of matching nodes with metadata
    - Relevance score
    - Node type and label
    
    **Search Features:**
    - Case-insensitive search
    - Matches node ID, label, and data fields
    - Type filtering
    - Relevance scoring
    
    **Example:**
    ```
    GET /api/graphs/1/search?query=vpc&node_type=resource&limit=10
    ```
    
    **Raises:**
    - 404: Repository or graph not found
    - 400: Invalid query parameters
    """
    logger.info(f"Searching graph for repository {repo_id}: query='{query}', type={node_type}")
    
    # Check repository exists
    repo = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail=f"Repository {repo_id} not found")
    
    # Get graph
    graph = db.query(Graph).filter(Graph.repository_id == repo_id).first()
    if not graph:
        raise HTTPException(
            status_code=404,
            detail=f"Graph not found for repository {repo_id}. Run analysis first."
        )
    
    # Search nodes
    query_lower = query.lower()
    results = []
    
    for node in graph.nodes:
        # Skip if type filter doesn't match
        if node_type and node.get('type') != node_type:
            continue
        
        # Calculate relevance score
        score = 0
        node_id = node.get('id', '').lower()
        node_label = node.get('label', '').lower()
        node_data = node.get('data', {})
        
        # Exact match in ID (highest score)
        if query_lower == node_id:
            score = 100
        # Starts with query in ID
        elif node_id.startswith(query_lower):
            score = 90
        # Contains query in ID
        elif query_lower in node_id:
            score = 70
        # Exact match in label
        elif query_lower == node_label:
            score = 80
        # Starts with query in label
        elif node_label.startswith(query_lower):
            score = 60
        # Contains query in label
        elif query_lower in node_label:
            score = 50
        # Search in data fields
        else:
            # Check various data fields
            searchable_fields = [
                str(node_data.get('name', '')).lower(),
                str(node_data.get('resourceType', '')).lower(),
                str(node_data.get('nodeType', '')).lower(),
                str(node_data.get('source', '')).lower(),
            ]
            
            for field in searchable_fields:
                if query_lower in field:
                    score = 30
                    break
        
        # Add to results if matched
        if score > 0:
            results.append({
                'node_id': node.get('id'),
                'label': node.get('label'),
                'type': node.get('type'),
                'data': node_data,
                'score': score,
                'metadata': node.get('metadata', {})
            })
    
    # Sort by relevance score (descending)
    results.sort(key=lambda x: x['score'], reverse=True)
    
    # Limit results
    results = results[:limit]
    
    logger.info(f"Found {len(results)} matching nodes")
    
    return results


@router.get("/{repo_id}/nodes/{node_id}", response_model=GraphNodeResponse)
def get_node_details(
    repo_id: int,
    node_id: str,
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific graph node
    
    **Parameters:**
    - **repo_id**: Repository ID
    - **node_id**: Node ID (e.g., "resource.aws_vpc.main")
    
    **Returns:**
    - Complete node data
    - Connected nodes (dependencies)
    - Incoming and outgoing edges
    
    **Raises:**
    - 404: Repository, graph, or node not found
    """
    logger.info(f"Fetching node details: repo={repo_id}, node={node_id}")
    
    # Check repository exists
    repo = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail=f"Repository {repo_id} not found")
    
    # Get graph
    graph = db.query(Graph).filter(Graph.repository_id == repo_id).first()
    if not graph:
        raise HTTPException(
            status_code=404,
            detail=f"Graph not found for repository {repo_id}"
        )
    
    # Find node
    node = next((n for n in graph.nodes if n.get('id') == node_id), None)
    if not node:
        raise HTTPException(
            status_code=404,
            detail=f"Node '{node_id}' not found in graph"
        )
    
    # Find connected edges
    outgoing_edges = [e for e in graph.edges if e.get('source') == node_id]
    incoming_edges = [e for e in graph.edges if e.get('target') == node_id]
    
    # Find connected nodes
    connected_node_ids = set()
    for edge in outgoing_edges + incoming_edges:
        connected_node_ids.add(edge.get('source'))
        connected_node_ids.add(edge.get('target'))
    connected_node_ids.discard(node_id)
    
    connected_nodes = [
        n for n in graph.nodes 
        if n.get('id') in connected_node_ids
    ]
    
    logger.info(
        f"Node details: {len(outgoing_edges)} outgoing, "
        f"{len(incoming_edges)} incoming, {len(connected_nodes)} connected"
    )
    
    return {
        'node': node,
        'outgoing_edges': outgoing_edges,
        'incoming_edges': incoming_edges,
        'connected_nodes': connected_nodes,
        'dependency_count': {
            'depends_on': len(outgoing_edges),
            'depended_by': len(incoming_edges)
        }
    }


# Made with Bob
