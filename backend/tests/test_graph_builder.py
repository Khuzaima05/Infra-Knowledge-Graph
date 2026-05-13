"""Unit tests for Graph Builder

Tests for building dependency graphs from parsed Terraform metadata.
"""

import pytest
from parser.parser_schemas import (
    ParsedResource,
    ParsedModule,
    ParsedVariable,
    ParsedOutput,
    ParsedProvider,
    RepositoryParseResult
)
from graph.graph_builder_v2 import GraphBuilder
from graph.graph_schemas import DependencyGraph


class TestGraphBuilder:
    """Test suite for GraphBuilder"""
    
    @pytest.fixture
    def sample_parse_result(self):
        """Create sample parsed Terraform data"""
        result = RepositoryParseResult(
            status="success",
            total_files=3,
            parsed_files=3,
            failed_files=0
        )
        
        # Add resources
        result.resources = [
            ParsedResource(
                type="aws_vpc",
                name="main",
                full_name="aws_vpc.main",
                provider="aws",
                metadata={"cidr_block": "10.0.0.0/16"}
            ),
            ParsedResource(
                type="aws_subnet",
                name="public",
                full_name="aws_subnet.public",
                provider="aws",
                metadata={
                    "vpc_id": "aws_vpc.main.id",
                    "cidr_block": "var.subnet_cidr"
                }
            ),
            ParsedResource(
                type="aws_security_group",
                name="main",
                full_name="aws_security_group.main",
                provider="aws",
                metadata={"vpc_id": "aws_vpc.main.id"}
            )
        ]
        
        # Add modules
        result.modules = [
            ParsedModule(
                name="vpc",
                source="./modules/vpc",
                version="1.0.0",
                metadata={"vpc_cidr": "var.vpc_cidr"}
            )
        ]
        
        # Add variables
        result.variables = [
            ParsedVariable(
                name="vpc_cidr",
                type="string",
                default_value="10.0.0.0/16",
                description="VPC CIDR block"
            ),
            ParsedVariable(
                name="subnet_cidr",
                type="string",
                default_value="10.0.1.0/24",
                description="Subnet CIDR block"
            )
        ]
        
        # Add outputs
        result.outputs = [
            ParsedOutput(
                name="vpc_id",
                value="aws_vpc.main.id",
                description="VPC ID"
            )
        ]
        
        # Add providers
        result.providers = [
            ParsedProvider(
                name="aws",
                version="~> 5.0",
                source="hashicorp/aws"
            )
        ]
        
        result.update_statistics()
        return result
    
    @pytest.fixture
    def builder(self):
        """Create GraphBuilder instance"""
        return GraphBuilder()
    
    def test_initialization(self, builder):
        """Test builder initialization"""
        assert builder.graph is not None
        assert len(builder.node_registry) == 0
        assert len(builder.edge_registry) == 0
    
    def test_add_resource_nodes(self, builder, sample_parse_result):
        """Test adding resource nodes"""
        resources = [r.model_dump() for r in sample_parse_result.resources]
        builder.add_resource_nodes(resources)
        
        assert len(builder.node_registry) == 3
        assert "aws_vpc.main" in builder.node_registry
        assert "aws_subnet.public" in builder.node_registry
        
        vpc_node = builder.node_registry["aws_vpc.main"]
        assert vpc_node.type == "resource"
        assert vpc_node.data["provider"] == "aws"
    
    def test_add_module_nodes(self, builder, sample_parse_result):
        """Test adding module nodes"""
        modules = [m.model_dump() for m in sample_parse_result.modules]
        builder.add_module_nodes(modules)
        
        assert len(builder.node_registry) == 1
        assert "module.vpc" in builder.node_registry
        
        module_node = builder.node_registry["module.vpc"]
        assert module_node.type == "module"
        assert module_node.data["source"] == "./modules/vpc"
    
    def test_add_variable_nodes(self, builder, sample_parse_result):
        """Test adding variable nodes"""
        variables = [v.model_dump() for v in sample_parse_result.variables]
        builder.add_variable_nodes(variables)
        
        assert len(builder.node_registry) == 2
        assert "var.vpc_cidr" in builder.node_registry
        assert "var.subnet_cidr" in builder.node_registry
        
        var_node = builder.node_registry["var.vpc_cidr"]
        assert var_node.type == "variable"
        assert var_node.data["defaultValue"] == "10.0.0.0/16"
    
    def test_add_output_nodes(self, builder, sample_parse_result):
        """Test adding output nodes"""
        outputs = [o.model_dump() for o in sample_parse_result.outputs]
        builder.add_output_nodes(outputs)
        
        assert len(builder.node_registry) == 1
        assert "output.vpc_id" in builder.node_registry
        
        output_node = builder.node_registry["output.vpc_id"]
        assert output_node.type == "output"
    
    def test_add_provider_nodes(self, builder, sample_parse_result):
        """Test adding provider nodes"""
        providers = [p.model_dump() for p in sample_parse_result.providers]
        builder.add_provider_nodes(providers)
        
        assert len(builder.node_registry) == 1
        assert "provider.aws" in builder.node_registry
        
        provider_node = builder.node_registry["provider.aws"]
        assert provider_node.type == "provider"
        assert provider_node.data["version"] == "~> 5.0"
    
    def test_resolve_references(self, builder, sample_parse_result):
        """Test reference resolution"""
        resources = [r.model_dump() for r in sample_parse_result.resources]
        modules = [m.model_dump() for m in sample_parse_result.modules]
        variables = [v.model_dump() for v in sample_parse_result.variables]
        
        # Add nodes first
        builder.add_resource_nodes(resources)
        builder.add_module_nodes(modules)
        builder.add_variable_nodes(variables)
        
        # Resolve references
        resolutions = builder.resolve_references(resources, modules)
        
        assert len(resolutions) > 0
        
        # Check that some references were resolved
        resolved_count = sum(1 for r in resolutions if r.resolved)
        assert resolved_count > 0
    
    def test_create_dependency_edges(self, builder, sample_parse_result):
        """Test dependency edge creation"""
        resources = [r.model_dump() for r in sample_parse_result.resources]
        modules = [m.model_dump() for m in sample_parse_result.modules]
        variables = [v.model_dump() for v in sample_parse_result.variables]
        
        # Add nodes
        builder.add_resource_nodes(resources)
        builder.add_module_nodes(modules)
        builder.add_variable_nodes(variables)
        
        # Resolve and create edges
        resolutions = builder.resolve_references(resources, modules)
        builder.create_dependency_edges(resolutions)
        
        assert len(builder.edge_registry) > 0
        
        # Check edge properties
        for edge in builder.edge_registry.values():
            assert edge.source in builder.node_registry
            assert edge.target in builder.node_registry
            assert edge.type in ["depends_on", "uses", "references", "provides", "contains"]
    
    def test_add_provider_edges(self, builder, sample_parse_result):
        """Test provider edge creation"""
        resources = [r.model_dump() for r in sample_parse_result.resources]
        providers = [p.model_dump() for p in sample_parse_result.providers]
        
        # Add nodes
        builder.add_resource_nodes(resources)
        builder.add_provider_nodes(providers)
        
        # Add provider edges
        builder.add_provider_edges(resources)
        
        # Check that provider edges were created
        provider_edges = [e for e in builder.edge_registry.values() if e.type == "provides"]
        assert len(provider_edges) > 0
    
    def test_compute_variable_lineage(self, builder, sample_parse_result):
        """Test variable lineage computation"""
        resources = [r.model_dump() for r in sample_parse_result.resources]
        variables = [v.model_dump() for v in sample_parse_result.variables]
        
        # Add nodes
        builder.add_resource_nodes(resources)
        builder.add_variable_nodes(variables)
        
        # Resolve references and create edges
        resolutions = builder.resolve_references(resources, [])
        builder.create_dependency_edges(resolutions)
        
        # Compute lineage
        lineage = builder.compute_variable_lineage()
        
        assert len(lineage) > 0
        
        # Check lineage properties
        for var_id, var_lineage in lineage.items():
            assert var_lineage.variable_id == var_id
            assert var_lineage.usage_count >= 0
    
    def test_build_graph(self, builder, sample_parse_result):
        """Test complete graph building"""
        graph = builder.build_graph(sample_parse_result)
        
        assert isinstance(graph, DependencyGraph)
        assert len(graph.nodes) > 0
        assert len(graph.edges) >= 0
        
        # Check statistics
        assert graph.statistics.total_nodes == len(graph.nodes)
        assert graph.statistics.total_edges == len(graph.edges)
        assert graph.statistics.total_nodes > 0
    
    def test_graph_statistics(self, builder, sample_parse_result):
        """Test graph statistics computation"""
        graph = builder.build_graph(sample_parse_result)
        stats = graph.statistics
        
        assert stats.total_nodes > 0
        assert stats.total_edges >= 0
        assert len(stats.node_types) > 0
        assert "resource" in stats.node_types
        assert "variable" in stats.node_types
        assert stats.avg_degree >= 0.0
    
    def test_to_json_format(self, builder, sample_parse_result):
        """Test JSON format conversion"""
        graph = builder.build_graph(sample_parse_result)
        json_data = graph.to_json_format()
        
        assert "nodes" in json_data
        assert "edges" in json_data
        assert "statistics" in json_data
        assert "metadata" in json_data
        
        assert isinstance(json_data["nodes"], list)
        assert isinstance(json_data["edges"], list)
        assert isinstance(json_data["statistics"], dict)
    
    def test_empty_parse_result(self, builder):
        """Test building graph from empty parse result"""
        empty_result = RepositoryParseResult(
            status="success",
            total_files=0,
            parsed_files=0,
            failed_files=0
        )
        
        graph = builder.build_graph(empty_result)
        
        assert len(graph.nodes) == 0
        assert len(graph.edges) == 0
        assert graph.statistics.total_nodes == 0
    
    def test_get_networkx_graph(self, builder, sample_parse_result):
        """Test getting NetworkX graph"""
        builder.build_graph(sample_parse_result)
        nx_graph = builder.get_networkx_graph()
        
        assert nx_graph is not None
        assert nx_graph.number_of_nodes() > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

# Made with Bob
