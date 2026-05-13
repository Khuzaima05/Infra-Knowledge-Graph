"""Enhanced Graph Builder for Terraform Dependencies

Builds dependency graphs from parsed Terraform metadata with:
- Reference resolution
- Variable lineage tracking
- Module/resource relationships
- NetworkX-based graph construction
"""

from typing import Dict, List, Any, Set, Tuple, Optional
import networkx as nx
from collections import defaultdict
from config.logger import logger

from parser.parser_schemas import RepositoryParseResult
from graph.graph_schemas import (
    GraphNode,
    GraphEdge,
    DependencyGraph,
    GraphStatistics,
    ReferenceResolution,
    VariableLineage,
    ModuleRelationship
)


class GraphBuilder:
    """
    Enhanced graph builder for Terraform infrastructure dependencies
    
    Features:
    - Resolves Terraform references
    - Creates dependency edges
    - Tracks variable lineage
    - Maps module/resource relationships
    - Uses NetworkX internally
    """
    
    def __init__(self):
        """Initialize graph builder"""
        self.graph = nx.DiGraph()
        self.node_registry: Dict[str, GraphNode] = {}
        self.edge_registry: Dict[str, GraphEdge] = {}
        self.reference_map: Dict[str, List[str]] = defaultdict(list)
        self.variable_lineage: Dict[str, VariableLineage] = {}
        self.module_relationships: Dict[str, ModuleRelationship] = {}
        logger.info("Initialized GraphBuilder")
    
    # ===== Node Creation =====
    
    def add_resource_nodes(self, resources: List[Dict[str, Any]]) -> None:
        """Add resource nodes to graph"""
        for resource in resources:
            node_id = resource.get('full_name', f"{resource['type']}.{resource['name']}")
            
            node = GraphNode(
                id=node_id,
                label=resource['name'],
                type="resource",
                data={
                    "nodeType": "resource",
                    "resourceType": resource['type'],
                    "name": resource['name'],
                    "provider": resource.get('provider', 'unknown'),
                    "filePath": resource.get('file_path')
                },
                metadata=resource.get('metadata', {})
            )
            
            self.node_registry[node_id] = node
            self.graph.add_node(node_id, **node.model_dump())
            logger.debug(f"Added resource node: {node_id}")
    
    def add_module_nodes(self, modules: List[Dict[str, Any]]) -> None:
        """Add module nodes to graph"""
        for module in modules:
            node_id = f"module.{module['name']}"
            
            node = GraphNode(
                id=node_id,
                label=module['name'],
                type="module",
                data={
                    "nodeType": "module",
                    "name": module['name'],
                    "source": module.get('source', ''),
                    "version": module.get('version'),
                    "filePath": module.get('file_path')
                },
                metadata=module.get('metadata', {})
            )
            
            self.node_registry[node_id] = node
            self.graph.add_node(node_id, **node.model_dump())
            
            # Initialize module relationship tracking
            self.module_relationships[node_id] = ModuleRelationship(
                module_id=node_id,
                module_name=module['name'],
                source=module.get('source', '')
            )
            
            logger.debug(f"Added module node: {node_id}")
    
    def add_variable_nodes(self, variables: List[Dict[str, Any]]) -> None:
        """Add variable nodes to graph"""
        for variable in variables:
            node_id = f"var.{variable['name']}"
            
            node = GraphNode(
                id=node_id,
                label=variable['name'],
                type="variable",
                data={
                    "nodeType": "variable",
                    "name": variable['name'],
                    "varType": variable.get('type', 'string'),
                    "defaultValue": variable.get('default_value'),
                    "description": variable.get('description', ''),
                    "sensitive": variable.get('sensitive', False),
                    "filePath": variable.get('file_path')
                },
                metadata=variable.get('metadata', {})
            )
            
            self.node_registry[node_id] = node
            self.graph.add_node(node_id, **node.model_dump())
            
            # Initialize variable lineage tracking
            self.variable_lineage[node_id] = VariableLineage(
                variable_id=node_id,
                variable_name=variable['name'],
                default_value=variable.get('default_value')
            )
            
            logger.debug(f"Added variable node: {node_id}")
    
    def add_output_nodes(self, outputs: List[Dict[str, Any]]) -> None:
        """Add output nodes to graph"""
        for output in outputs:
            node_id = f"output.{output['name']}"
            
            node = GraphNode(
                id=node_id,
                label=output['name'],
                type="output",
                data={
                    "nodeType": "output",
                    "name": output['name'],
                    "description": output.get('description', ''),
                    "sensitive": output.get('sensitive', False),
                    "filePath": output.get('file_path')
                },
                metadata=output.get('metadata', {})
            )
            
            self.node_registry[node_id] = node
            self.graph.add_node(node_id, **node.model_dump())
            logger.debug(f"Added output node: {node_id}")
    
    def add_provider_nodes(self, providers: List[Dict[str, Any]]) -> None:
        """Add provider nodes to graph"""
        for provider in providers:
            node_id = f"provider.{provider['name']}"
            if provider.get('alias'):
                node_id = f"provider.{provider['name']}.{provider['alias']}"
            
            node = GraphNode(
                id=node_id,
                label=provider['name'],
                type="provider",
                data={
                    "nodeType": "provider",
                    "name": provider['name'],
                    "version": provider.get('version'),
                    "source": provider.get('source'),
                    "alias": provider.get('alias'),
                    "filePath": provider.get('file_path')
                },
                metadata=provider.get('metadata', {})
            )
            
            self.node_registry[node_id] = node
            self.graph.add_node(node_id, **node.model_dump())
            logger.debug(f"Added provider node: {node_id}")
    
    def add_local_nodes(self, locals_list: List[Dict[str, Any]]) -> None:
        """Add local value nodes to graph"""
        for local in locals_list:
            node_id = f"local.{local['name']}"
            
            node = GraphNode(
                id=node_id,
                label=local['name'],
                type="local",
                data={
                    "nodeType": "local",
                    "name": local['name'],
                    "value": local.get('value'),
                    "filePath": local.get('file_path')
                },
                metadata={}
            )
            
            self.node_registry[node_id] = node
            self.graph.add_node(node_id, **node.model_dump())
            logger.debug(f"Added local node: {node_id}")
    
    def add_data_source_nodes(self, data_sources: List[Dict[str, Any]]) -> None:
        """Add data source nodes to graph"""
        for data_source in data_sources:
            node_id = data_source.get('full_name', f"data.{data_source['type']}.{data_source['name']}")
            
            node = GraphNode(
                id=node_id,
                label=data_source['name'],
                type="data_source",
                data={
                    "nodeType": "data_source",
                    "dataType": data_source['type'],
                    "name": data_source['name'],
                    "provider": data_source.get('provider', 'unknown'),
                    "filePath": data_source.get('file_path')
                },
                metadata=data_source.get('metadata', {})
            )
            
            self.node_registry[node_id] = node
            self.graph.add_node(node_id, **node.model_dump())
            logger.debug(f"Added data source node: {node_id}")
    
    # ===== Edge Creation & Reference Resolution =====
    
    def resolve_references(self, resources: List[Dict[str, Any]], modules: List[Dict[str, Any]]) -> List[ReferenceResolution]:
        """
        Resolve references in resource and module metadata
        
        Scans metadata for references to variables, other resources, modules, etc.
        """
        resolutions = []
        
        # Resolve resource references
        for resource in resources:
            source_id = resource.get('full_name', f"{resource['type']}.{resource['name']}")
            metadata = resource.get('metadata', {})
            
            refs = self._extract_references_from_metadata(metadata)
            for ref in refs:
                target_id = self._resolve_reference_target(ref)
                if target_id and self.graph.has_node(target_id):
                    resolution = ReferenceResolution(
                        reference_type=ref['type'],
                        source_id=source_id,
                        target_id=target_id,
                        resolved=True,
                        context=ref.get('context')
                    )
                    resolutions.append(resolution)
                    self.reference_map[source_id].append(target_id)
        
        # Resolve module references
        for module in modules:
            source_id = f"module.{module['name']}"
            metadata = module.get('metadata', {})
            
            refs = self._extract_references_from_metadata(metadata)
            for ref in refs:
                target_id = self._resolve_reference_target(ref)
                if target_id and self.graph.has_node(target_id):
                    resolution = ReferenceResolution(
                        reference_type=ref['type'],
                        source_id=source_id,
                        target_id=target_id,
                        resolved=True,
                        context=ref.get('context')
                    )
                    resolutions.append(resolution)
                    self.reference_map[source_id].append(target_id)
        
        logger.info(f"Resolved {len(resolutions)} references")
        return resolutions
    
    def _extract_references_from_metadata(self, metadata: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extract references from metadata values"""
        import re
        references = []
        
        def scan_value(value: Any, context: str = ""):
            if isinstance(value, str):
                # Variable references
                for match in re.finditer(r'var\.([a-zA-Z_][a-zA-Z0-9_]*)', value):
                    references.append({
                        'type': 'variable',
                        'name': match.group(1),
                        'context': context
                    })
                
                # Module references
                for match in re.finditer(r'module\.([a-zA-Z_][a-zA-Z0-9_]*)\.([a-zA-Z_][a-zA-Z0-9_]*)', value):
                    references.append({
                        'type': 'module_output',
                        'module': match.group(1),
                        'output': match.group(2),
                        'context': context
                    })
                
                # Resource references
                for match in re.finditer(r'([a-z_]+)\.([a-z_0-9]+)\.([a-zA-Z_][a-zA-Z0-9_]*)', value):
                    references.append({
                        'type': 'resource',
                        'resource_type': match.group(1),
                        'resource_name': match.group(2),
                        'attribute': match.group(3),
                        'context': context
                    })
                
                # Local references
                for match in re.finditer(r'local\.([a-zA-Z_][a-zA-Z0-9_]*)', value):
                    references.append({
                        'type': 'local',
                        'name': match.group(1),
                        'context': context
                    })
                
                # Data source references
                for match in re.finditer(r'data\.([a-z_]+)\.([a-z_0-9]+)', value):
                    references.append({
                        'type': 'data_source',
                        'data_type': match.group(1),
                        'data_name': match.group(2),
                        'context': context
                    })
            
            elif isinstance(value, dict):
                for k, v in value.items():
                    scan_value(v, f"{context}.{k}" if context else k)
            
            elif isinstance(value, list):
                for i, item in enumerate(value):
                    scan_value(item, f"{context}[{i}]")
        
        scan_value(metadata)
        return references
    
    def _resolve_reference_target(self, ref: Dict[str, str]) -> Optional[str]:
        """Resolve reference to target node ID"""
        ref_type = ref.get('type')
        
        if ref_type == 'variable':
            return f"var.{ref['name']}"
        
        elif ref_type == 'module_output':
            return f"module.{ref['module']}"
        
        elif ref_type == 'resource':
            return f"{ref['resource_type']}.{ref['resource_name']}"
        
        elif ref_type == 'local':
            return f"local.{ref['name']}"
        
        elif ref_type == 'data_source':
            return f"data.{ref['data_type']}.{ref['data_name']}"
        
        return None
    
    def create_dependency_edges(self, resolutions: List[ReferenceResolution]) -> None:
        """Create dependency edges from resolved references"""
        for resolution in resolutions:
            if not resolution.resolved:
                continue
            
            source = resolution.source_id
            target = resolution.target_id
            
            if not (self.graph.has_node(source) and self.graph.has_node(target)):
                continue
            
            # Determine edge type
            edge_type = self._determine_edge_type(resolution.reference_type)
            
            edge_id = f"{source}->{target}"
            edge = GraphEdge(
                id=edge_id,
                source=source,
                target=target,
                type=edge_type,
                data={
                    "relationshipType": edge_type,
                    "referenceType": resolution.reference_type,
                    "context": resolution.context
                }
            )
            
            self.edge_registry[edge_id] = edge
            self.graph.add_edge(source, target, **edge.model_dump())
            
            # Update variable lineage
            if resolution.reference_type == 'variable':
                if target in self.variable_lineage:
                    self.variable_lineage[target].used_by.append(source)
                    self.variable_lineage[target].usage_count += 1
            
            # Update module relationships
            if source.startswith('module.'):
                if source in self.module_relationships:
                    if resolution.reference_type == 'variable':
                        self.module_relationships[source].variables_used.append(target)
        
        logger.info(f"Created {len(self.edge_registry)} dependency edges")
    
    def _determine_edge_type(self, reference_type: str) -> str:
        """Determine edge type from reference type"""
        type_mapping = {
            'variable': 'uses',
            'module_output': 'references',
            'resource': 'depends_on',
            'local': 'uses',
            'data_source': 'uses'
        }
        return type_mapping.get(reference_type, 'depends_on')
    
    def add_provider_edges(self, resources: List[Dict[str, Any]]) -> None:
        """Add edges from resources to their providers"""
        for resource in resources:
            provider = resource.get('provider')
            if not provider:
                continue
            
            source_id = resource.get('full_name', f"{resource['type']}.{resource['name']}")
            target_id = f"provider.{provider}"
            
            if self.graph.has_node(source_id) and self.graph.has_node(target_id):
                edge_id = f"{source_id}->{target_id}"
                edge = GraphEdge(
                    id=edge_id,
                    source=source_id,
                    target=target_id,
                    type="provides",
                    data={"relationshipType": "uses_provider"},
                    weight=0.5
                )
                
                self.edge_registry[edge_id] = edge
                self.graph.add_edge(source_id, target_id, **edge.model_dump())
        
        logger.debug("Added provider edges")
    
    def add_module_containment_edges(self, modules: List[Dict[str, Any]], resources: List[Dict[str, Any]]) -> None:
        """Add containment edges showing which resources belong to which modules"""
        # This would require parsing module source paths and matching resources
        # For now, we'll track module relationships
        for module in modules:
            module_id = f"module.{module['name']}"
            if module_id in self.module_relationships:
                # Track resources that might belong to this module
                # This is a simplified version - full implementation would parse module sources
                pass
    
    # ===== Variable Lineage =====
    
    def compute_variable_lineage(self) -> Dict[str, VariableLineage]:
        """Compute variable usage lineage and depth"""
        for var_id, lineage in self.variable_lineage.items():
            if not self.graph.has_node(var_id):
                continue
            
            # Compute lineage depth (shortest path from variable to any output)
            min_depth = float('inf')
            for node_id in self.graph.nodes():
                if node_id.startswith('output.'):
                    try:
                        if nx.has_path(self.graph, var_id, node_id):
                            path_length = nx.shortest_path_length(self.graph, var_id, node_id)
                            min_depth = min(min_depth, path_length)
                    except nx.NetworkXNoPath:
                        pass
            
            if min_depth != float('inf'):
                lineage.lineage_depth = int(min_depth)
        
        logger.info(f"Computed lineage for {len(self.variable_lineage)} variables")
        return self.variable_lineage
    
    # ===== Graph Building =====
    
    def build_graph(self, parse_result: RepositoryParseResult) -> DependencyGraph:
        """
        Build complete dependency graph from parsed Terraform metadata
        
        Args:
            parse_result: Parsed Terraform repository result
            
        Returns:
            DependencyGraph with nodes and edges
        """
        logger.info("Building dependency graph")
        
        # Convert parsed results to dict format
        resources = [r.model_dump() for r in parse_result.resources]
        modules = [m.model_dump() for m in parse_result.modules]
        variables = [v.model_dump() for v in parse_result.variables]
        outputs = [o.model_dump() for o in parse_result.outputs]
        providers = [p.model_dump() for p in parse_result.providers]
        locals_list = [l.model_dump() for l in parse_result.locals]
        data_sources = [d.model_dump() for d in parse_result.data_sources]
        
        # Add all nodes
        self.add_resource_nodes(resources)
        self.add_module_nodes(modules)
        self.add_variable_nodes(variables)
        self.add_output_nodes(outputs)
        self.add_provider_nodes(providers)
        self.add_local_nodes(locals_list)
        self.add_data_source_nodes(data_sources)
        
        # Resolve references and create edges
        resolutions = self.resolve_references(resources, modules)
        self.create_dependency_edges(resolutions)
        self.add_provider_edges(resources)
        self.add_module_containment_edges(modules, resources)
        
        # Compute variable lineage
        self.compute_variable_lineage()
        
        # Build final graph
        graph = DependencyGraph(
            nodes=list(self.node_registry.values()),
            edges=list(self.edge_registry.values()),
            statistics=self._compute_statistics(),
            metadata={
                "repository_status": parse_result.status,
                "total_files_parsed": parse_result.parsed_files,
                "parse_errors": len(parse_result.errors)
            }
        )
        
        logger.info(f"Graph built: {len(graph.nodes)} nodes, {len(graph.edges)} edges")
        return graph
    
    def _compute_statistics(self) -> GraphStatistics:
        """Compute graph statistics"""
        node_types: Dict[str, int] = defaultdict(int)
        for node in self.node_registry.values():
            node_types[node.type] += 1
        
        edge_types: Dict[str, int] = defaultdict(int)
        for edge in self.edge_registry.values():
            edge_types[edge.type] += 1
        
        # Check for cycles
        has_cycles = not nx.is_directed_acyclic_graph(self.graph)
        
        # Compute max depth
        max_depth = 0
        if not has_cycles:
            try:
                max_depth = nx.dag_longest_path_length(self.graph)
            except:
                pass
        
        # Compute average degree
        avg_degree = 0.0
        if self.graph.number_of_nodes() > 0:
            degrees = [d for n, d in self.graph.degree()]
            total_degree = sum(degrees)
            avg_degree = total_degree / self.graph.number_of_nodes()
        
        # Count connected components
        undirected = self.graph.to_undirected()
        connected_components = nx.number_connected_components(undirected)
        
        return GraphStatistics(
            total_nodes=self.graph.number_of_nodes(),
            total_edges=self.graph.number_of_edges(),
            node_types=dict(node_types),
            edge_types=dict(edge_types),
            connected_components=connected_components,
            has_cycles=has_cycles,
            max_depth=max_depth,
            avg_degree=round(avg_degree, 2)
        )
    
    def get_networkx_graph(self) -> nx.DiGraph:
        """Get the underlying NetworkX graph"""
        return self.graph

# Made with Bob
