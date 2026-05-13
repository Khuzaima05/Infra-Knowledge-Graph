from typing import Dict, List, Any, Set, Tuple
import networkx as nx
from collections import defaultdict


class GraphBuilder:
    """Build dependency graphs from parsed Terraform infrastructure"""
    
    def __init__(self):
        self.graph = nx.DiGraph()
        self.nodes_metadata = {}
        self.relationships = []
    
    def add_module_nodes(self, modules: List[Dict[str, Any]]) -> None:
        """Add module nodes to graph"""
        for module in modules:
            node_id = f"module.{module['name']}"
            self.graph.add_node(
                node_id,
                node_type="module",
                name=module['name'],
                source=module.get('source', ''),
                version=module.get('version'),
                metadata=module.get('metadata', {})
            )
    
    def add_resource_nodes(self, resources: List[Dict[str, Any]]) -> None:
        """Add resource nodes to graph"""
        for resource in resources:
            node_id = resource['full_name']
            self.graph.add_node(
                node_id,
                node_type="resource",
                type=resource['type'],
                name=resource['name'],
                provider=resource.get('provider'),
                metadata=resource.get('metadata', {})
            )
    
    def add_variable_nodes(self, variables: List[Dict[str, Any]]) -> None:
        """Add variable nodes to graph"""
        for variable in variables:
            node_id = f"var.{variable['name']}"
            self.graph.add_node(
                node_id,
                node_type="variable",
                name=variable['name'],
                type=variable.get('type', 'string'),
                default_value=variable.get('default_value'),
                description=variable.get('description', ''),
                metadata=variable.get('metadata', {})
            )
    
    def add_output_nodes(self, outputs: List[Dict[str, Any]]) -> None:
        """Add output nodes to graph"""
        for output in outputs:
            node_id = f"output.{output['name']}"
            self.graph.add_node(
                node_id,
                node_type="output",
                name=output['name'],
                description=output.get('description', ''),
                metadata=output.get('metadata', {})
            )
    
    def add_provider_nodes(self, providers: List[Dict[str, Any]]) -> None:
        """Add provider nodes to graph"""
        for provider in providers:
            node_id = f"provider.{provider['name']}"
            self.graph.add_node(
                node_id,
                node_type="provider",
                name=provider['name'],
                version=provider.get('version'),
                alias=provider.get('alias'),
                metadata=provider.get('metadata', {})
            )
    
    def add_local_nodes(self, content: str) -> None:
        """Add local value nodes detected from content"""
        import re
        
        # Find locals block
        locals_pattern = r'locals\s*\{([^}]+)\}'
        match = re.search(locals_pattern, content, re.DOTALL)
        
        if match:
            locals_block = match.group(1)
            # Extract local names
            local_names = re.findall(r'(\w+)\s*=', locals_block)
            
            for local_name in local_names:
                node_id = f"local.{local_name}"
                self.graph.add_node(
                    node_id,
                    node_type="local",
                    name=local_name,
                    metadata={}
                )
    
    def add_edges_from_references(self, references: List[Dict[str, Any]]) -> None:
        """
        Build edges based on detected references
        A reference creates a dependency edge from the resource using the reference
        to the referenced component
        """
        for ref in references:
            ref_type = ref.get('type')
            
            # Variable reference: something uses a var
            if ref_type == 'variable':
                target_id = f"var.{ref['target']}"
                if self.graph.has_node(target_id):
                    # We don't know source yet, just track the reference
                    self.relationships.append({
                        'type': 'uses',
                        'target': target_id,
                        'source_type': 'reference'
                    })
            
            # Module output reference
            elif ref_type == 'module_output':
                target_id = f"module.{ref['module']}"
                if self.graph.has_node(target_id):
                    self.relationships.append({
                        'type': 'references_output',
                        'target': target_id,
                        'output': ref['output'],
                        'source_type': 'reference'
                    })
            
            # Resource attribute reference
            elif ref_type == 'resource_attribute':
                target_id = f"{ref['resource_type']}.{ref['resource_name']}"
                if self.graph.has_node(target_id):
                    self.relationships.append({
                        'type': 'depends_on',
                        'target': target_id,
                        'attribute': ref['attribute'],
                        'source_type': 'reference'
                    })
            
            # Local reference
            elif ref_type == 'local':
                target_id = f"local.{ref['target']}"
                self.relationships.append({
                    'type': 'uses',
                    'target': target_id,
                    'source_type': 'reference'
                })
            
            # Data source reference
            elif ref_type == 'data_source':
                target_id = f"data.{ref['data_type']}.{ref['data_name']}"
                self.relationships.append({
                    'type': 'uses',
                    'target': target_id,
                    'source_type': 'reference'
                })
    
    def add_provider_edges(self, resources: List[Dict[str, Any]]) -> None:
        """Add edges from resources to their providers"""
        for resource in resources:
            if resource.get('provider'):
                source_id = resource['full_name']
                target_id = f"provider.{resource['provider']}"
                
                if self.graph.has_node(source_id) and self.graph.has_node(target_id):
                    self.graph.add_edge(
                        source_id,
                        target_id,
                        relationship_type='uses_provider',
                        weight=0.5
                    )
    
    def build_graph(
        self,
        modules: List[Dict[str, Any]],
        resources: List[Dict[str, Any]],
        variables: List[Dict[str, Any]],
        outputs: List[Dict[str, Any]],
        providers: List[Dict[str, Any]],
        references: List[Dict[str, Any]],
        file_content: str = ""
    ) -> Dict[str, Any]:
        """
        Build complete dependency graph from parsed Terraform
        Returns graph data in JSON format for visualization
        """
        # Add all nodes
        self.add_module_nodes(modules)
        self.add_resource_nodes(resources)
        self.add_variable_nodes(variables)
        self.add_output_nodes(outputs)
        self.add_provider_nodes(providers)
        if file_content:
            self.add_local_nodes(file_content)
        
        # Add edges from references
        self.add_edges_from_references(references)
        
        # Add provider edges
        self.add_provider_edges(resources)
        
        # Convert to visualization format
        return self.to_visualization_format()
    
    def to_visualization_format(self) -> Dict[str, Any]:
        """Convert NetworkX graph to visualization-friendly JSON format"""
        nodes = []
        edges = []
        
        # Add nodes with positions (will be calculated by frontend)
        for node_id, attrs in self.graph.nodes(data=True):
            node_type = attrs.get('node_type', 'unknown')
            
            node_obj = {
                'id': node_id,
                'label': attrs.get('name', node_id),
                'type': node_type,
                'data': {
                    'nodeType': node_type,
                    'name': attrs.get('name', node_id),
                }
            }
            
            # Add type-specific data
            if node_type == 'resource':
                node_obj['data'].update({
                    'resourceType': attrs.get('type'),
                    'provider': attrs.get('provider'),
                })
            elif node_type == 'variable':
                node_obj['data'].update({
                    'varType': attrs.get('type'),
                    'default': attrs.get('default_value'),
                    'description': attrs.get('description'),
                })
            elif node_type == 'module':
                node_obj['data'].update({
                    'source': attrs.get('source'),
                    'version': attrs.get('version'),
                })
            elif node_type == 'output':
                node_obj['data'].update({
                    'description': attrs.get('description'),
                })
            elif node_type == 'provider':
                node_obj['data'].update({
                    'version': attrs.get('version'),
                    'alias': attrs.get('alias'),
                })
            
            # Add metadata if exists
            if attrs.get('metadata'):
                node_obj['metadata'] = attrs['metadata']
            
            nodes.append(node_obj)
        
        # Add edges
        for source, target, attrs in self.graph.edges(data=True):
            edge_obj = {
                'id': f"{source}->{target}",
                'source': source,
                'target': target,
                'type': 'default',
                'data': {
                    'relationshipType': attrs.get('relationship_type', 'depends_on')
                }
            }
            edges.append(edge_obj)
        
        return {
            'nodes': nodes,
            'edges': edges,
            'nodeCount': len(nodes),
            'edgeCount': len(edges),
            'graphType': 'dependency'
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get graph statistics"""
        node_types = defaultdict(int)
        for node_id, attrs in self.graph.nodes(data=True):
            node_type = attrs.get('node_type', 'unknown')
            node_types[node_type] += 1
        
        relationship_types = defaultdict(int)
        for source, target, attrs in self.graph.edges(data=True):
            rel_type = attrs.get('relationship_type', 'unknown')
            relationship_types[rel_type] += 1
        
        return {
            'total_nodes': self.graph.number_of_nodes(),
            'total_edges': self.graph.number_of_edges(),
            'node_types': dict(node_types),
            'relationship_types': dict(relationship_types),
            'connected_components': nx.number_connected_components(self.graph.to_undirected()),
            'cycles': len(list(nx.simple_cycles(self.graph))) if nx.is_directed_acyclic_graph(self.graph) == False else 0
        }


class DependencyAnalyzer:
    """Analyze dependencies and relationships in infrastructure graph"""
    
    def __init__(self, graph: nx.DiGraph):
        self.graph = graph
    
    def get_resource_dependencies(self, resource_id: str) -> Dict[str, Any]:
        """Get all dependencies for a resource"""
        if not self.graph.has_node(resource_id):
            return {}
        
        predecessors = list(self.graph.predecessors(resource_id))
        successors = list(self.graph.successors(resource_id))
        
        return {
            'resource': resource_id,
            'depends_on': predecessors,
            'depended_by': successors,
            'total_dependencies': len(predecessors),
            'total_dependents': len(successors)
        }
    
    def find_cycles(self) -> List[List[str]]:
        """Find circular dependencies in infrastructure"""
        try:
            cycles = list(nx.simple_cycles(self.graph))
            return cycles
        except:
            return []
    
    def get_critical_path(self) -> List[str]:
        """Find longest path in DAG (critical path for deployment)"""
        try:
            if nx.is_directed_acyclic_graph(self.graph):
                return nx.dag_longest_path(self.graph)
            else:
                return []
        except:
            return []
    
    def get_isolated_components(self) -> List[List[str]]:
        """Find isolated components in infrastructure"""
        undirected = self.graph.to_undirected()
        components = list(nx.connected_components(undirected))
        return [list(comp) for comp in components if len(comp) > 1]
