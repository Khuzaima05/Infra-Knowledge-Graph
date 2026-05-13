"""Utility functions for Terraform parsing

Helper functions for value normalization, provider extraction, and reference detection.
"""

import re
import json
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path


def normalize_value(value: Any) -> Any:
    """
    Normalize Python value to JSON-compatible format
    
    Args:
        value: Value to normalize
        
    Returns:
        JSON-serializable value
    """
    if isinstance(value, (str, int, float, bool, type(None))):
        return value
    elif isinstance(value, (list, tuple)):
        return [normalize_value(v) for v in value]
    elif isinstance(value, dict):
        return {k: normalize_value(v) for k, v in value.items()}
    else:
        return str(value)


def extract_provider_from_resource_type(resource_type: str) -> str:
    """
    Extract provider name from resource type
    
    Examples:
        aws_vpc -> aws
        azurerm_virtual_network -> azurerm
        google_compute_network -> google
    
    Args:
        resource_type: Resource type string
        
    Returns:
        Provider name
    """
    if not resource_type:
        return "unknown"
    
    parts = resource_type.split('_')
    if len(parts) >= 1:
        return parts[0]
    return "unknown"


def detect_variable_references(content: str) -> List[Dict[str, str]]:
    """
    Detect var.* references in Terraform code
    
    Args:
        content: Terraform file content
        
    Returns:
        List of variable references
    """
    references = []
    pattern = r'var\.([a-zA-Z_][a-zA-Z0-9_]*)'
    
    for match in re.finditer(pattern, content):
        references.append({
            'type': 'variable',
            'target': match.group(1),
            'position': match.start()
        })
    
    return references


def detect_module_references(content: str) -> List[Dict[str, str]]:
    """
    Detect module.* references in Terraform code
    
    Args:
        content: Terraform file content
        
    Returns:
        List of module output references
    """
    references = []
    pattern = r'module\.([a-zA-Z_][a-zA-Z0-9_]*)\.([a-zA-Z_][a-zA-Z0-9_]*)'
    
    for match in re.finditer(pattern, content):
        references.append({
            'type': 'module_output',
            'module': match.group(1),
            'output': match.group(2),
            'position': match.start()
        })
    
    return references


def detect_resource_references(content: str) -> List[Dict[str, str]]:
    """
    Detect resource attribute references in Terraform code
    
    Args:
        content: Terraform file content
        
    Returns:
        List of resource references
    """
    references = []
    # Match patterns like: aws_vpc.main.id, aws_subnet.public.*.id
    pattern = r'([a-z_]+)\.([a-z_0-9]+)\.([a-zA-Z_*][a-zA-Z0-9_]*)'
    
    for match in re.finditer(pattern, content):
        references.append({
            'type': 'resource_attribute',
            'resource_type': match.group(1),
            'resource_name': match.group(2),
            'attribute': match.group(3),
            'position': match.start()
        })
    
    return references


def detect_local_references(content: str) -> List[Dict[str, str]]:
    """
    Detect local.* references in Terraform code
    
    Args:
        content: Terraform file content
        
    Returns:
        List of local value references
    """
    references = []
    pattern = r'local\.([a-zA-Z_][a-zA-Z0-9_]*)'
    
    for match in re.finditer(pattern, content):
        references.append({
            'type': 'local',
            'target': match.group(1),
            'position': match.start()
        })
    
    return references


def detect_data_source_references(content: str) -> List[Dict[str, str]]:
    """
    Detect data.* references in Terraform code
    
    Args:
        content: Terraform file content
        
    Returns:
        List of data source references
    """
    references = []
    pattern = r'data\.([a-z_]+)\.([a-z_0-9]+)'
    
    for match in re.finditer(pattern, content):
        references.append({
            'type': 'data_source',
            'data_type': match.group(1),
            'data_name': match.group(2),
            'position': match.start()
        })
    
    return references


def detect_all_references(content: str) -> List[Dict[str, Any]]:
    """
    Detect all types of references in Terraform code
    
    Args:
        content: Terraform file content
        
    Returns:
        List of all detected references
    """
    references = []
    
    references.extend(detect_variable_references(content))
    references.extend(detect_module_references(content))
    references.extend(detect_resource_references(content))
    references.extend(detect_local_references(content))
    references.extend(detect_data_source_references(content))
    
    # Sort by position
    references.sort(key=lambda x: x.get('position', 0))
    
    return references


def is_terraform_file(file_path: str) -> bool:
    """
    Check if file is a Terraform file
    
    Args:
        file_path: Path to file
        
    Returns:
        True if Terraform file, False otherwise
    """
    path = Path(file_path)
    return path.suffix in ['.tf', '.tfvars']


def should_exclude_directory(dir_name: str, exclude_dirs: List[str]) -> bool:
    """
    Check if directory should be excluded from scanning
    
    Args:
        dir_name: Directory name
        exclude_dirs: List of directories to exclude
        
    Returns:
        True if should exclude, False otherwise
    """
    return dir_name in exclude_dirs or dir_name.startswith('.')


def get_file_size_mb(file_path: str) -> float:
    """
    Get file size in megabytes
    
    Args:
        file_path: Path to file
        
    Returns:
        File size in MB
    """
    try:
        size_bytes = Path(file_path).stat().st_size
        return size_bytes / (1024 * 1024)
    except Exception:
        return 0.0


def safe_read_file(file_path: str, encoding: str = 'utf-8') -> Tuple[bool, str, Optional[str]]:
    """
    Safely read file content with error handling
    
    Args:
        file_path: Path to file
        encoding: File encoding
        
    Returns:
        Tuple of (success, content, error_message)
    """
    try:
        with open(file_path, 'r', encoding=encoding, errors='ignore') as f:
            content = f.read()
        return (True, content, None)
    except FileNotFoundError:
        return (False, "", f"File not found: {file_path}")
    except PermissionError:
        return (False, "", f"Permission denied: {file_path}")
    except Exception as e:
        return (False, "", f"Error reading file: {str(e)}")


def extract_block_metadata(block_config: Dict[str, Any], exclude_keys: List[str]) -> Dict[str, Any]:
    """
    Extract metadata from HCL block, excluding specified keys
    
    Args:
        block_config: Block configuration dictionary
        exclude_keys: Keys to exclude from metadata
        
    Returns:
        Metadata dictionary
    """
    metadata = {}
    for key, value in block_config.items():
        if key not in exclude_keys:
            metadata[key] = normalize_value(value)
    return metadata


def format_full_resource_name(resource_type: str, resource_name: str) -> str:
    """
    Format full resource identifier
    
    Args:
        resource_type: Resource type
        resource_name: Resource name
        
    Returns:
        Full resource name (type.name)
    """
    return f"{resource_type}.{resource_name}"


def format_full_data_source_name(data_type: str, data_name: str) -> str:
    """
    Format full data source identifier
    
    Args:
        data_type: Data source type
        data_name: Data source name
        
    Returns:
        Full data source name (data.type.name)
    """
    return f"data.{data_type}.{data_name}"


def parse_terraform_version(version_str: str) -> Optional[str]:
    """
    Parse and normalize Terraform version constraint
    
    Args:
        version_str: Version constraint string
        
    Returns:
        Normalized version string or None
    """
    if not version_str:
        return None
    
    # Remove whitespace
    version_str = version_str.strip()
    
    # Common patterns: ">= 1.0", "~> 5.0", "= 1.2.3"
    if version_str:
        return version_str
    
    return None


def extract_depends_on(config: Dict[str, Any]) -> List[str]:
    """
    Extract depends_on list from configuration
    
    Args:
        config: Configuration dictionary
        
    Returns:
        List of dependencies
    """
    depends_on = config.get('depends_on', [])
    
    if isinstance(depends_on, list):
        return [str(dep) for dep in depends_on]
    elif isinstance(depends_on, str):
        return [depends_on]
    
    return []


def is_sensitive_value(config: Dict[str, Any]) -> bool:
    """
    Check if value is marked as sensitive
    
    Args:
        config: Configuration dictionary
        
    Returns:
        True if sensitive, False otherwise
    """
    sensitive = config.get('sensitive', False)
    return bool(sensitive)


def extract_validation_rules(config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """
    Extract validation rules from variable configuration
    
    Args:
        config: Variable configuration
        
    Returns:
        Validation rules dictionary or None
    """
    validation = config.get('validation')
    
    if validation and isinstance(validation, dict):
        return normalize_value(validation)
    elif validation and isinstance(validation, list):
        # Multiple validation blocks
        return {'rules': [normalize_value(v) for v in validation]}
    
    return None


def categorize_parse_status(total_files: int, parsed_files: int, failed_files: int) -> str:
    """
    Determine overall parse status based on results
    
    Args:
        total_files: Total number of files
        parsed_files: Successfully parsed files
        failed_files: Failed to parse files
        
    Returns:
        Status string: 'success', 'partial', or 'error'
    """
    if total_files == 0:
        return "error"
    elif failed_files == 0:
        return "success"
    elif parsed_files > 0:
        return "partial"
    else:
        return "error"


def get_line_number(content: str, search_string: str) -> Optional[int]:
    """
    Find line number of a string in content
    
    Args:
        content: File content
        search_string: String to search for
        
    Returns:
        Line number (1-indexed) or None
    """
    try:
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            if search_string in line:
                return i
    except Exception:
        pass
    
    return None

# Made with Bob
