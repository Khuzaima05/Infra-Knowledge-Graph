"""Enhanced Terraform Parser with python-hcl2

Modular, type-safe parser for Terraform files with comprehensive error handling.
"""

import os
from typing import Dict, List, Any, Optional
from pathlib import Path
import hcl2
from config.logger import logger

from parser.parser_schemas import (
    ParsedResource,
    ParsedModule,
    ParsedVariable,
    ParsedOutput,
    ParsedProvider,
    ParsedLocal,
    ParsedDataSource,
    ParsedReference,
    FileParseResult,
    RepositoryParseResult,
    ParserConfig
)
from parser.parser_utils import (
    normalize_value,
    extract_provider_from_resource_type,
    detect_all_references,
    is_terraform_file,
    should_exclude_directory,
    get_file_size_mb,
    safe_read_file,
    extract_block_metadata,
    format_full_resource_name,
    format_full_data_source_name,
    extract_depends_on,
    is_sensitive_value,
    extract_validation_rules,
    categorize_parse_status,
    get_line_number
)


class TerraformParser:
    """
    Enhanced Terraform parser using python-hcl2
    
    Features:
    - Recursive file scanning
    - Typed output schemas
    - Malformed file handling
    - Reference detection
    - Modular architecture
    """
    
    def __init__(self, config: Optional[ParserConfig] = None):
        """
        Initialize parser with configuration
        
        Args:
            config: Parser configuration (uses defaults if None)
        """
        self.config = config or ParserConfig()
        logger.info("Initialized TerraformParser with config")
    
    # ===== File Discovery =====
    
    def find_terraform_files(self, repo_path: str) -> List[str]:
        """
        Recursively find all Terraform files in repository
        
        Args:
            repo_path: Path to repository root
            
        Returns:
            List of absolute file paths
        """
        tf_files = []
        repo_path_obj = Path(repo_path)
        
        if not repo_path_obj.exists():
            logger.error(f"Repository path does not exist: {repo_path}")
            return tf_files
        
        try:
            for root, dirs, files in os.walk(repo_path):
                # Filter out excluded directories
                dirs[:] = [d for d in dirs if not should_exclude_directory(d, self.config.exclude_dirs)]
                
                for file in files:
                    file_path = os.path.join(root, file)
                    
                    # Check if Terraform file
                    if is_terraform_file(file_path):
                        # Check file size
                        if get_file_size_mb(file_path) <= self.config.max_file_size_mb:
                            tf_files.append(file_path)
                        else:
                            logger.warning(f"Skipping large file: {file_path}")
            
            logger.info(f"Found {len(tf_files)} Terraform files in {repo_path}")
            return sorted(tf_files)
        
        except Exception as e:
            logger.error(f"Error scanning directory {repo_path}: {e}")
            return tf_files
    
    # ===== Single File Parsing =====
    
    def parse_file(self, file_path: str, repo_root: Optional[str] = None) -> FileParseResult:
        """
        Parse a single Terraform file
        
        Args:
            file_path: Absolute path to file
            repo_root: Repository root path (for relative paths)
            
        Returns:
            FileParseResult with parsed components
        """
        # Calculate relative path
        if repo_root:
            rel_path = os.path.relpath(file_path, repo_root)
        else:
            rel_path = os.path.basename(file_path)
        
        result = FileParseResult(
            file_path=rel_path,
            status="success"
        )
        
        # Read file content
        success, content, error = safe_read_file(file_path)
        
        if not success:
            result.status = "error"
            result.error = error
            logger.error(f"Failed to read {rel_path}: {error}")
            return result
        
        # Parse HCL2
        try:
            parsed_hcl = hcl2.loads(content)
            
            # Extract all components
            result.resources = self._extract_resources(parsed_hcl, rel_path, content)
            result.modules = self._extract_modules(parsed_hcl, rel_path, content)
            result.variables = self._extract_variables(parsed_hcl, rel_path, content)
            result.outputs = self._extract_outputs(parsed_hcl, rel_path, content)
            result.providers = self._extract_providers(parsed_hcl, rel_path, content)
            result.locals = self._extract_locals(parsed_hcl, rel_path, content)
            result.data_sources = self._extract_data_sources(parsed_hcl, rel_path, content)
            
            # Extract references if enabled
            if self.config.extract_references:
                result.references = self._extract_references(content, rel_path)
            
            logger.debug(f"Successfully parsed {rel_path}")
        
        except Exception as e:
            result.status = "error"
            result.error = f"HCL2 parse error: {str(e)}"
            logger.error(f"Failed to parse {rel_path}: {e}")
            
            # Try to extract what we can even with errors
            if self.config.continue_on_error:
                result.status = "warning"
                logger.info(f"Continuing with partial parse of {rel_path}")
        
        return result
    
    # ===== Component Extraction Methods =====
    
    def _extract_resources(self, parsed_hcl: Dict[str, Any], file_path: str, content: str) -> List[ParsedResource]:
        """Extract resource blocks from parsed HCL"""
        resources = []
        
        if 'resource' not in parsed_hcl:
            return resources
        
        try:
            for resource_type, resource_blocks in parsed_hcl['resource'].items():
                if not isinstance(resource_blocks, dict):
                    continue
                
                provider = extract_provider_from_resource_type(resource_type)
                
                for resource_name, resource_config in resource_blocks.items():
                    if not isinstance(resource_config, dict):
                        continue
                    
                    resource = ParsedResource(
                        type=resource_type,
                        name=resource_name,
                        full_name=format_full_resource_name(resource_type, resource_name),
                        provider=provider,
                        metadata=extract_block_metadata(resource_config, []),
                        file_path=file_path,
                        line_number=get_line_number(content, f'resource "{resource_type}" "{resource_name}"')
                    )
                    
                    resources.append(resource)
        
        except Exception as e:
            logger.warning(f"Error extracting resources from {file_path}: {e}")
        
        return resources
    
    def _extract_modules(self, parsed_hcl: Dict[str, Any], file_path: str, content: str) -> List[ParsedModule]:
        """Extract module blocks from parsed HCL"""
        modules = []
        
        if 'module' not in parsed_hcl:
            return modules
        
        try:
            for module_name, module_config in parsed_hcl['module'].items():
                if not isinstance(module_config, dict):
                    continue
                
                module = ParsedModule(
                    name=module_name,
                    source=module_config.get('source', ''),
                    version=module_config.get('version'),
                    metadata=extract_block_metadata(module_config, ['source', 'version']),
                    file_path=file_path,
                    line_number=get_line_number(content, f'module "{module_name}"')
                )
                
                modules.append(module)
        
        except Exception as e:
            logger.warning(f"Error extracting modules from {file_path}: {e}")
        
        return modules
    
    def _extract_variables(self, parsed_hcl: Dict[str, Any], file_path: str, content: str) -> List[ParsedVariable]:
        """Extract variable blocks from parsed HCL"""
        variables = []
        
        if 'variable' not in parsed_hcl:
            return variables
        
        try:
            for var_name, var_config in parsed_hcl['variable'].items():
                if not isinstance(var_config, dict):
                    continue
                
                variable = ParsedVariable(
                    name=var_name,
                    type=str(var_config.get('type', 'string')),
                    default_value=normalize_value(var_config.get('default')),
                    description=var_config.get('description', ''),
                    sensitive=is_sensitive_value(var_config),
                    validation=extract_validation_rules(var_config),
                    metadata=extract_block_metadata(var_config, ['type', 'default', 'description', 'sensitive', 'validation']),
                    file_path=file_path,
                    line_number=get_line_number(content, f'variable "{var_name}"')
                )
                
                variables.append(variable)
        
        except Exception as e:
            logger.warning(f"Error extracting variables from {file_path}: {e}")
        
        return variables
    
    def _extract_outputs(self, parsed_hcl: Dict[str, Any], file_path: str, content: str) -> List[ParsedOutput]:
        """Extract output blocks from parsed HCL"""
        outputs = []
        
        if 'output' not in parsed_hcl:
            return outputs
        
        try:
            for output_name, output_config in parsed_hcl['output'].items():
                if not isinstance(output_config, dict):
                    continue
                
                output = ParsedOutput(
                    name=output_name,
                    value=normalize_value(output_config.get('value')),
                    description=output_config.get('description', ''),
                    sensitive=is_sensitive_value(output_config),
                    depends_on=extract_depends_on(output_config),
                    metadata=extract_block_metadata(output_config, ['value', 'description', 'sensitive', 'depends_on']),
                    file_path=file_path,
                    line_number=get_line_number(content, f'output "{output_name}"')
                )
                
                outputs.append(output)
        
        except Exception as e:
            logger.warning(f"Error extracting outputs from {file_path}: {e}")
        
        return outputs
    
    def _extract_providers(self, parsed_hcl: Dict[str, Any], file_path: str, content: str) -> List[ParsedProvider]:
        """Extract provider blocks from parsed HCL"""
        providers = []
        provider_names = set()
        
        try:
            # Extract from terraform.required_providers
            if 'terraform' in parsed_hcl:
                terraform_block = parsed_hcl['terraform']
                if isinstance(terraform_block, dict) and 'required_providers' in terraform_block:
                    required_providers = terraform_block['required_providers']
                    
                    if isinstance(required_providers, dict):
                        for provider_name, provider_config in required_providers.items():
                            if isinstance(provider_config, dict):
                                provider = ParsedProvider(
                                    name=provider_name,
                                    version=provider_config.get('version'),
                                    source=provider_config.get('source'),
                                    metadata=extract_block_metadata(provider_config, ['version', 'source']),
                                    file_path=file_path,
                                    line_number=get_line_number(content, f'"{provider_name}"')
                                )
                                providers.append(provider)
                                provider_names.add(provider_name)
            
            # Extract from provider blocks
            if 'provider' in parsed_hcl:
                for provider_name, provider_config in parsed_hcl['provider'].items():
                    if not isinstance(provider_config, dict):
                        continue
                    
                    # Skip if already added from required_providers
                    if provider_name in provider_names:
                        continue
                    
                    provider = ParsedProvider(
                        name=provider_name,
                        alias=provider_config.get('alias'),
                        metadata=extract_block_metadata(provider_config, ['alias']),
                        file_path=file_path,
                        line_number=get_line_number(content, f'provider "{provider_name}"')
                    )
                    providers.append(provider)
                    provider_names.add(provider_name)
        
        except Exception as e:
            logger.warning(f"Error extracting providers from {file_path}: {e}")
        
        return providers
    
    def _extract_locals(self, parsed_hcl: Dict[str, Any], file_path: str, content: str) -> List[ParsedLocal]:
        """Extract local value blocks from parsed HCL"""
        locals_list = []
        
        if 'locals' not in parsed_hcl:
            return locals_list
        
        try:
            locals_block = parsed_hcl['locals']
            if isinstance(locals_block, dict):
                for local_name, local_value in locals_block.items():
                    local = ParsedLocal(
                        name=local_name,
                        value=normalize_value(local_value),
                        file_path=file_path,
                        line_number=get_line_number(content, f'{local_name} =')
                    )
                    locals_list.append(local)
        
        except Exception as e:
            logger.warning(f"Error extracting locals from {file_path}: {e}")
        
        return locals_list
    
    def _extract_data_sources(self, parsed_hcl: Dict[str, Any], file_path: str, content: str) -> List[ParsedDataSource]:
        """Extract data source blocks from parsed HCL"""
        data_sources = []
        
        if 'data' not in parsed_hcl:
            return data_sources
        
        try:
            for data_type, data_blocks in parsed_hcl['data'].items():
                if not isinstance(data_blocks, dict):
                    continue
                
                provider = extract_provider_from_resource_type(data_type)
                
                for data_name, data_config in data_blocks.items():
                    if not isinstance(data_config, dict):
                        continue
                    
                    data_source = ParsedDataSource(
                        type=data_type,
                        name=data_name,
                        full_name=format_full_data_source_name(data_type, data_name),
                        provider=provider,
                        metadata=extract_block_metadata(data_config, []),
                        file_path=file_path,
                        line_number=get_line_number(content, f'data "{data_type}" "{data_name}"')
                    )
                    
                    data_sources.append(data_source)
        
        except Exception as e:
            logger.warning(f"Error extracting data sources from {file_path}: {e}")
        
        return data_sources
    
    def _extract_references(self, content: str, file_path: str) -> List[ParsedReference]:
        """Extract all references from file content"""
        references = []
        
        try:
            raw_refs = detect_all_references(content)
            
            for ref in raw_refs:
                reference = ParsedReference(
                    type=ref['type'],
                    target=ref.get('target'),
                    source_file=file_path
                )
                references.append(reference)
        
        except Exception as e:
            logger.warning(f"Error extracting references from {file_path}: {e}")
        
        return references
    
    # ===== Repository Parsing =====
    
    def parse_repository(self, repo_path: str) -> RepositoryParseResult:
        """
        Parse entire repository and extract all Terraform components
        
        Args:
            repo_path: Path to repository root
            
        Returns:
            RepositoryParseResult with all parsed components
        """
        logger.info(f"Starting repository parse: {repo_path}")
        
        result = RepositoryParseResult(status="success")
        
        # Find all Terraform files
        tf_files = self.find_terraform_files(repo_path)
        result.total_files = len(tf_files)
        
        if result.total_files == 0:
            result.status = "error"
            result.errors.append("No Terraform files found in repository")
            logger.warning(f"No Terraform files found in {repo_path}")
            return result
        
        # Parse each file
        for file_path in tf_files:
            file_result = self.parse_file(file_path, repo_root=repo_path)
            result.file_results.append(file_result)
            
            if file_result.status == "success":
                result.parsed_files += 1
                
                # Aggregate components
                result.resources.extend(file_result.resources)
                result.modules.extend(file_result.modules)
                result.variables.extend(file_result.variables)
                result.outputs.extend(file_result.outputs)
                result.providers.extend(file_result.providers)
                result.locals.extend(file_result.locals)
                result.data_sources.extend(file_result.data_sources)
                result.references.extend(file_result.references)
            
            elif file_result.status == "error":
                result.failed_files += 1
                if file_result.error:
                    result.errors.append(f"{file_result.file_path}: {file_result.error}")
            
            elif file_result.status == "warning":
                result.parsed_files += 1  # Partial success
                if file_result.error:
                    result.errors.append(f"{file_result.file_path}: {file_result.error}")
        
        # Determine overall status
        result.status = categorize_parse_status(
            result.total_files,
            result.parsed_files,
            result.failed_files
        )
        
        # Update statistics
        result.update_statistics()
        
        logger.info(
            f"Repository parse complete: {result.parsed_files}/{result.total_files} files parsed, "
            f"{result.failed_files} failed"
        )
        
        return result
    
    # ===== Output Formatting =====
    
    def format_output(self, result: RepositoryParseResult) -> Dict[str, Any]:
        """
        Format parse result to match required output structure
        
        Args:
            result: RepositoryParseResult
            
        Returns:
            Dictionary with formatted output
        """
        return {
            "resources": [r.model_dump() for r in result.resources],
            "modules": [m.model_dump() for m in result.modules],
            "variables": [v.model_dump() for v in result.variables],
            "outputs": [o.model_dump() for o in result.outputs],
            "providers": [p.model_dump() for p in result.providers],
            "locals": [l.model_dump() for l in result.locals],
            "data_sources": [d.model_dump() for d in result.data_sources],
            "statistics": result.statistics,
            "status": result.status,
            "errors": result.errors
        }

# Made with Bob
