"""Architecture Summary Generator

Generates human-readable infrastructure summaries from parsed Terraform metadata.
Does NOT use external AI APIs - purely metadata-based analysis.

Features:
- Resource counting and categorization
- Provider usage analysis
- Module relationship mapping
- Networking overview
- Infrastructure complexity insights
"""

from typing import Dict, List, Any, Optional, Set, Tuple
from collections import defaultdict, Counter
from sqlalchemy.orm import Session
from datetime import datetime

from models.models import (
    Repository, Resource, Module, Provider, 
    Variable, Output, Relationship, Graph, Summary
)
from config.logger import logger


class SummaryGenerator:
    """Generates architecture summaries from Terraform metadata"""
    
    def __init__(self, db: Session):
        """Initialize summary generator"""
        self.db = db
        logger.info("Initialized SummaryGenerator")
    
    def generate_summary(self, repository_id: int) -> Summary:
        """
        Generate comprehensive architecture summary
        
        Args:
            repository_id: Repository ID to analyze
            
        Returns:
            Summary object with architecture insights
        """
        logger.info(f"Generating summary for repository {repository_id}")
        
        # Fetch repository data
        repo = self.db.query(Repository).filter(Repository.id == repository_id).first()
        if not repo:
            raise ValueError(f"Repository {repository_id} not found")
        
        # Gather all metadata
        resources = self.db.query(Resource).filter(Resource.repository_id == repository_id).all()
        modules = self.db.query(Module).filter(Module.repository_id == repository_id).all()
        providers = self.db.query(Provider).filter(Provider.repository_id == repository_id).all()
        variables = self.db.query(Variable).filter(Variable.repository_id == repository_id).all()
        outputs = self.db.query(Output).filter(Output.repository_id == repository_id).all()
        relationships = self.db.query(Relationship).filter(Relationship.repository_id == repository_id).all()
        graph = self.db.query(Graph).filter(Graph.repository_id == repository_id).first()
        
        # Generate summary components
        title = self._generate_title(repo, resources, modules, providers)
        architecture_description = self._generate_architecture_description(
            repo, resources, modules, providers, variables, outputs, relationships, graph
        )
        key_components = self._identify_key_components(resources, modules, providers)
        deployment_overview = self._generate_deployment_overview(resources, modules, providers)
        
        # Create or update summary
        summary = self.db.query(Summary).filter(Summary.repository_id == repository_id).first()
        if summary:
            summary.title = title
            summary.architecture_description = architecture_description
            summary.key_components = key_components
            summary.deployment_overview = deployment_overview
            summary.updated_at = datetime.utcnow()
        else:
            summary = Summary(
                repository_id=repository_id,
                title=title,
                architecture_description=architecture_description,
                key_components=key_components,
                deployment_overview=deployment_overview
            )
            self.db.add(summary)
        
        self.db.commit()
        self.db.refresh(summary)
        
        logger.info(f"Generated summary for repository {repository_id}")
        return summary
    
    def _generate_title(
        self, 
        repo: Repository, 
        resources: List[Resource],
        modules: List[Module],
        providers: List[Provider]
    ) -> str:
        """Generate concise summary title"""
        resource_count = len(resources)
        module_count = len(modules)
        
        # Get primary provider
        provider_names = [p.name for p in providers]
        primary_provider = self._get_primary_provider(provider_names)
        
        if module_count > 0:
            return f"{resource_count} Terraform resources across {module_count} modules using {primary_provider}"
        else:
            return f"{resource_count} Terraform resources using {primary_provider}"
    
    def _generate_architecture_description(
        self,
        repo: Repository,
        resources: List[Resource],
        modules: List[Module],
        providers: List[Provider],
        variables: List[Variable],
        outputs: List[Output],
        relationships: List[Relationship],
        graph: Optional[Graph]
    ) -> str:
        """Generate detailed architecture description"""
        sections = []
        
        # Overview section
        overview = self._generate_overview_section(repo, resources, modules, providers)
        sections.append(overview)
        
        # Provider analysis
        provider_section = self._generate_provider_section(providers, resources)
        sections.append(provider_section)
        
        # Module analysis
        if modules:
            module_section = self._generate_module_section(modules, resources)
            sections.append(module_section)
        
        # Networking analysis
        networking_section = self._generate_networking_section(resources)
        if networking_section:
            sections.append(networking_section)
        
        # Complexity insights
        complexity_section = self._generate_complexity_section(
            resources, modules, relationships, graph
        )
        sections.append(complexity_section)
        
        # Configuration section
        config_section = self._generate_configuration_section(variables, outputs)
        sections.append(config_section)
        
        return "\n\n".join(sections)
    
    def _generate_overview_section(
        self,
        repo: Repository,
        resources: List[Resource],
        modules: List[Module],
        providers: List[Provider]
    ) -> str:
        """Generate overview section"""
        resource_count = len(resources)
        module_count = len(modules)
        provider_count = len(set(p.name for p in providers))
        
        # Categorize resources
        resource_types = Counter(r.type for r in resources)
        top_resources = resource_types.most_common(3)
        
        overview = f"**Overview**\n\n"
        overview += f"This repository contains {resource_count} Terraform resources"
        
        if module_count > 0:
            overview += f" organized across {module_count} modules"
        
        overview += f", utilizing {provider_count} cloud provider(s). "
        
        if top_resources:
            resource_list = ", ".join([f"{count} {rtype}" for rtype, count in top_resources])
            overview += f"The most common resource types are: {resource_list}."
        
        return overview
    
    def _generate_provider_section(
        self,
        providers: List[Provider],
        resources: List[Resource]
    ) -> str:
        """Generate provider usage analysis"""
        provider_names = [p.name for p in providers]
        provider_counts = Counter(provider_names)
        
        # Count resources per provider
        resource_providers = Counter(r.provider for r in resources if r.provider)
        
        section = f"**Provider Usage**\n\n"
        
        if len(provider_counts) == 1:
            provider_name = list(provider_counts.keys())[0]
            resource_count = resource_providers.get(provider_name, 0)
            section += f"This infrastructure is built entirely on {provider_name.upper()}, "
            section += f"with {resource_count} resources deployed. "
        else:
            section += f"This is a multi-cloud deployment using {len(provider_counts)} providers:\n\n"
            for provider, count in provider_counts.most_common():
                resource_count = resource_providers.get(provider, 0)
                section += f"- **{provider.upper()}**: {resource_count} resources\n"
        
        # Provider versions
        versioned_providers = [p for p in providers if p.version]
        if versioned_providers:
            section += f"\n{len(versioned_providers)} provider(s) have explicit version constraints for reproducibility."
        
        return section
    
    def _generate_module_section(
        self,
        modules: List[Module],
        resources: List[Resource]
    ) -> str:
        """Generate module relationship analysis"""
        section = f"**Module Architecture**\n\n"
        
        module_count = len(modules)
        section += f"The infrastructure is modularized into {module_count} reusable components:\n\n"
        
        # Categorize modules by source
        local_modules = [m for m in modules if m.source and not m.source.startswith(('http', 'git', 'registry'))]
        remote_modules = [m for m in modules if m.source and m.source.startswith(('http', 'git', 'registry'))]
        
        if local_modules:
            section += f"- **{len(local_modules)} local modules** for custom infrastructure patterns\n"
        
        if remote_modules:
            section += f"- **{len(remote_modules)} remote modules** from external sources\n"
        
        # Module complexity
        module_names = [m.name for m in modules]
        section += f"\nKey modules include: {', '.join(module_names[:5])}"
        if len(module_names) > 5:
            section += f" and {len(module_names) - 5} more"
        section += "."
        
        return section
    
    def _generate_networking_section(self, resources: List[Resource]) -> Optional[str]:
        """Generate networking overview"""
        # Identify networking resources
        network_keywords = ['vpc', 'subnet', 'network', 'route', 'gateway', 'firewall', 'security_group', 'nat']
        network_resources = [
            r for r in resources 
            if any(keyword in r.type.lower() for keyword in network_keywords)
        ]
        
        if not network_resources:
            return None
        
        section = f"**Networking Overview**\n\n"
        section += f"The infrastructure includes {len(network_resources)} networking components:\n\n"
        
        # Categorize network resources
        network_types = Counter(r.type for r in network_resources)
        for net_type, count in network_types.most_common():
            section += f"- {count} {net_type}\n"
        
        # Identify VPCs/Networks
        vpcs = [r for r in network_resources if 'vpc' in r.type.lower() or 'network' in r.type.lower()]
        if vpcs:
            section += f"\nThe deployment spans {len(vpcs)} virtual network(s), "
            section += "providing network isolation and security boundaries."
        
        return section
    
    def _generate_complexity_section(
        self,
        resources: List[Resource],
        modules: List[Module],
        relationships: List[Relationship],
        graph: Optional[Graph]
    ) -> str:
        """Generate infrastructure complexity insights"""
        section = f"**Infrastructure Complexity**\n\n"
        
        # Resource diversity
        unique_types = len(set(r.type for r in resources))
        section += f"The infrastructure uses {unique_types} distinct resource types, "
        
        # Dependency analysis
        dependency_count = len(relationships)
        if dependency_count > 0:
            section += f"with {dependency_count} explicit dependencies between components. "
        else:
            section += "with minimal explicit dependencies. "
        
        # Graph metrics
        if graph and graph.node_count > 0:
            avg_connections = graph.edge_count / graph.node_count if graph.node_count > 0 else 0
            section += f"\n\nThe dependency graph contains {graph.node_count} nodes and {graph.edge_count} edges, "
            section += f"with an average of {avg_connections:.1f} connections per component. "
            
            if avg_connections > 3:
                section += "This indicates a highly interconnected infrastructure with complex dependencies."
            elif avg_connections > 1.5:
                section += "This indicates moderate coupling between infrastructure components."
            else:
                section += "This indicates loosely coupled infrastructure with clear separation of concerns."
        
        # Module reusability
        if modules:
            section += f"\n\nThe use of {len(modules)} modules promotes code reusability and maintainability."
        
        return section
    
    def _generate_configuration_section(
        self,
        variables: List[Variable],
        outputs: List[Output]
    ) -> str:
        """Generate configuration section"""
        section = f"**Configuration**\n\n"
        
        var_count = len(variables)
        output_count = len(outputs)
        
        section += f"The infrastructure is parameterized with {var_count} input variable(s) "
        section += f"and exposes {output_count} output value(s). "
        
        # Variable analysis
        typed_vars = [v for v in variables if v.type]
        defaulted_vars = [v for v in variables if v.default_value]
        
        if typed_vars:
            section += f"\n\n{len(typed_vars)} variables have explicit type constraints, "
        if defaulted_vars:
            section += f"and {len(defaulted_vars)} have default values for easier deployment."
        
        # Output analysis
        if outputs:
            section += f"\n\nOutputs provide access to {output_count} key infrastructure values "
            section += "for integration with other systems or modules."
        
        return section
    
    def _generate_deployment_overview(
        self,
        resources: List[Resource],
        modules: List[Module],
        providers: List[Provider]
    ) -> str:
        """Generate deployment overview"""
        overview = []
        
        # Provider summary
        provider_names = list(set(p.name for p in providers))
        if len(provider_names) == 1:
            overview.append(f"Single-cloud deployment on {provider_names[0].upper()}")
        else:
            overview.append(f"Multi-cloud deployment across {', '.join(p.upper() for p in provider_names)}")
        
        # Module structure
        if modules:
            overview.append(f"Modular architecture with {len(modules)} components")
        else:
            overview.append("Monolithic configuration")
        
        # Resource scale
        resource_count = len(resources)
        if resource_count < 10:
            overview.append("Small-scale infrastructure")
        elif resource_count < 50:
            overview.append("Medium-scale infrastructure")
        else:
            overview.append("Large-scale infrastructure")
        
        return " | ".join(overview)
    
    def _identify_key_components(
        self,
        resources: List[Resource],
        modules: List[Module],
        providers: List[Provider]
    ) -> List[Dict[str, str]]:
        """Identify key infrastructure components"""
        components = []
        
        # Provider components
        for provider in providers:
            resource_count = len([r for r in resources if r.provider == provider.name])
            components.append({
                "name": f"{provider.name.upper()} Provider",
                "description": f"Manages {resource_count} cloud resources",
                "type": "provider"
            })
        
        # Module components
        for module in modules[:5]:  # Top 5 modules
            components.append({
                "name": module.name,
                "description": f"Module from {module.source or 'local source'}",
                "type": "module"
            })
        
        # Critical resource types
        resource_types = Counter(r.type for r in resources)
        for resource_type, count in resource_types.most_common(5):
            components.append({
                "name": resource_type,
                "description": f"{count} instances deployed",
                "type": "resource"
            })
        
        return components
    
    def _get_primary_provider(self, provider_names: List[str]) -> str:
        """Determine primary provider"""
        if not provider_names:
            return "unknown provider"
        
        provider_counts = Counter(provider_names)
        primary = provider_counts.most_common(1)[0][0]
        
        if len(provider_counts) == 1:
            return f"{primary.upper()}"
        else:
            return f"{primary.upper()} and {len(provider_counts) - 1} other provider(s)"

# Made with Bob
