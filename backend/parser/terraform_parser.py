import os
import json
import re
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import hcl2


class TerraformParser:
    """Parse Terraform HCL2 files and extract infrastructure components"""
    
    def __init__(self, workspace_dir: str = "./cloned_repos"):
        self.workspace_dir = workspace_dir
        os.makedirs(workspace_dir, exist_ok=True)
    
    def find_terraform_files(self, repo_path: str) -> List[str]:
        """Recursively find all .tf files in repository"""
        tf_files = []
        for root, dirs, files in os.walk(repo_path):
            # Skip .terraform directories
            if '.terraform' in dirs:
                dirs.remove('.terraform')
            
            for file in files:
                if file.endswith('.tf'):
                    tf_files.append(os.path.join(root, file))
        
        return tf_files
    
    def parse_file(self, file_path: str) -> Dict[str, Any]:
        """Parse a single Terraform file and extract all components"""
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Parse HCL2
            parsed = hcl2.loads(content)
            
            return {
                'status': 'success',
                'content': content,
                'parsed': parsed,
                'error': None
            }
        except Exception as e:
            return {
                'status': 'error',
                'content': '',
                'parsed': {},
                'error': str(e)
            }
    
    def extract_modules(self, parsed_hcl: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract module blocks from parsed HCL"""
        modules = []
        
        if 'module' not in parsed_hcl:
            return modules
        
        for module_name, module_config in parsed_hcl['module'].items():
            module_data = {
                'name': module_name,
                'source': module_config.get('source', ''),
                'version': module_config.get('version', None),
                'metadata': {}
            }
            
            # Extract variables passed to module
            for key, value in module_config.items():
                if key not in ['source', 'version']:
                    module_data['metadata'][key] = self._serialize_value(value)
            
            modules.append(module_data)
        
        return modules
    
    def extract_resources(self, parsed_hcl: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract resource blocks from parsed HCL"""
        resources = []
        
        if 'resource' not in parsed_hcl:
            return resources
        
        for resource_type, resource_blocks in parsed_hcl['resource'].items():
            provider = self._extract_provider_from_resource_type(resource_type)
            
            for resource_name, resource_config in resource_blocks.items():
                resource_data = {
                    'type': resource_type,
                    'name': resource_name,
                    'full_name': f"{resource_type}.{resource_name}",
                    'provider': provider,
                    'metadata': {}
                }
                
                # Store resource configuration
                for key, value in resource_config.items():
                    resource_data['metadata'][key] = self._serialize_value(value)
                
                resources.append(resource_data)
        
        return resources
    
    def extract_variables(self, parsed_hcl: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract variable blocks from parsed HCL"""
        variables = []
        
        if 'variable' not in parsed_hcl:
            return variables
        
        for var_name, var_config in parsed_hcl['variable'].items():
            var_data = {
                'name': var_name,
                'type': var_config.get('type', 'string'),
                'default_value': self._serialize_value(var_config.get('default', None)),
                'description': var_config.get('description', ''),
                'metadata': {k: v for k, v in var_config.items() 
                            if k not in ['type', 'default', 'description']}
            }
            
            variables.append(var_data)
        
        return variables
    
    def extract_outputs(self, parsed_hcl: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract output blocks from parsed HCL"""
        outputs = []
        
        if 'output' not in parsed_hcl:
            return outputs
        
        for output_name, output_config in parsed_hcl['output'].items():
            output_data = {
                'name': output_name,
                'value': self._serialize_value(output_config.get('value', None)),
                'description': output_config.get('description', ''),
                'metadata': {k: v for k, v in output_config.items() 
                            if k not in ['value', 'description']}
            }
            
            outputs.append(output_data)
        
        return outputs
    
    def extract_providers(self, parsed_hcl: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract provider blocks from parsed HCL"""
        providers = []
        
        if 'terraform' in parsed_hcl and 'required_providers' in parsed_hcl['terraform']:
            for provider_name, config in parsed_hcl['terraform']['required_providers'].items():
                provider_data = {
                    'name': provider_name,
                    'version': config.get('version', None) if isinstance(config, dict) else None,
                    'metadata': config if isinstance(config, dict) else {}
                }
                providers.append(provider_data)
        
        if 'provider' in parsed_hcl:
            for provider_name, config in parsed_hcl['provider'].items():
                # Check if already added
                if not any(p['name'] == provider_name for p in providers):
                    provider_data = {
                        'name': provider_name,
                        'version': None,
                        'alias': config.get('alias', None) if isinstance(config, dict) else None,
                        'metadata': config if isinstance(config, dict) else {}
                    }
                    providers.append(provider_data)
        
        return providers
    
    def detect_references(self, content: str) -> List[Dict[str, Any]]:
        """
        Detect variable and resource references in HCL content using regex patterns
        Patterns: var.name, module.name.output, aws_resource.name.id, local.name
        """
        references = []
        
        # Pattern for var.* references
        var_refs = re.findall(r'var\.([a-zA-Z_][a-zA-Z0-9_]*)', content)
        for var_name in var_refs:
            references.append({
                'type': 'variable',
                'target': var_name,
                'source_type': 'reference'
            })
        
        # Pattern for module.* references (module outputs)
        module_refs = re.findall(r'module\.([a-zA-Z_][a-zA-Z0-9_]*)\.([a-zA-Z_][a-zA-Z0-9_]*)', content)
        for module_name, output_name in module_refs:
            references.append({
                'type': 'module_output',
                'module': module_name,
                'output': output_name,
                'source_type': 'reference'
            })
        
        # Pattern for resource references
        resource_refs = re.findall(
            r'([a-z_]+)\.([a-z_0-9]+)\.(id|arn|name|endpoint|address)',
            content
        )
        for resource_type, resource_name, attribute in resource_refs:
            references.append({
                'type': 'resource_attribute',
                'resource_type': resource_type,
                'resource_name': resource_name,
                'attribute': attribute,
                'source_type': 'reference'
            })
        
        # Pattern for local.* references
        local_refs = re.findall(r'local\.([a-zA-Z_][a-zA-Z0-9_]*)', content)
        for local_name in local_refs:
            references.append({
                'type': 'local',
                'target': local_name,
                'source_type': 'reference'
            })
        
        # Pattern for data source references
        data_refs = re.findall(r'data\.([a-z_]+)\.([a-z_0-9]+)', content)
        for data_type, data_name in data_refs:
            references.append({
                'type': 'data_source',
                'data_type': data_type,
                'data_name': data_name,
                'source_type': 'reference'
            })
        
        return references
    
    def parse_repository(self, repo_path: str) -> Dict[str, Any]:
        """Parse entire repository and extract all components"""
        result = {
            'status': 'success',
            'files': [],
            'modules': [],
            'resources': [],
            'variables': [],
            'outputs': [],
            'providers': [],
            'references': [],
            'errors': []
        }
        
        # Find all Terraform files
        tf_files = self.find_terraform_files(repo_path)
        
        if not tf_files:
            result['status'] = 'warning'
            result['errors'].append('No Terraform files found')
            return result
        
        for file_path in tf_files:
            rel_path = os.path.relpath(file_path, repo_path)
            
            # Parse file
            parse_result = self.parse_file(file_path)
            
            file_data = {
                'path': rel_path,
                'status': parse_result['status'],
                'error': parse_result['error']
            }
            
            result['files'].append(file_data)
            
            if parse_result['status'] == 'success':
                parsed = parse_result['parsed']
                content = parse_result['content']
                
                # Extract components
                result['modules'].extend(self.extract_modules(parsed))
                result['resources'].extend(self.extract_resources(parsed))
                result['variables'].extend(self.extract_variables(parsed))
                result['outputs'].extend(self.extract_outputs(parsed))
                result['providers'].extend(self.extract_providers(parsed))
                
                # Detect references
                result['references'].extend(self.detect_references(content))
            else:
                result['errors'].append(f"Failed to parse {rel_path}: {parse_result['error']}")
        
        return result
    
    @staticmethod
    def _extract_provider_from_resource_type(resource_type: str) -> str:
        """Extract provider name from resource type (e.g., aws_vpc -> aws)"""
        parts = resource_type.split('_')
        if len(parts) >= 1:
            return parts[0]
        return 'unknown'
    
    @staticmethod
    def _serialize_value(value: Any) -> Any:
        """Serialize Python value to JSON-compatible format"""
        if isinstance(value, (str, int, float, bool, type(None))):
            return value
        elif isinstance(value, (list, tuple)):
            return [TerraformParser._serialize_value(v) for v in value]
        elif isinstance(value, dict):
            return {k: TerraformParser._serialize_value(v) for k, v in value.items()}
        else:
            return str(value)
