# Terraform Parser Documentation

## Overview

The Terraform Parser is a comprehensive, modular parsing engine built with `python-hcl2` that extracts infrastructure components from Terraform files. It features typed schemas, robust error handling, and support for malformed files.

## Features

✅ **Comprehensive Parsing**
- Resources
- Modules
- Variables
- Outputs
- Providers
- Local values
- Data sources

✅ **Robust Error Handling**
- Graceful handling of malformed files
- Detailed error reporting
- Continue-on-error mode
- File-level and repository-level status

✅ **Type-Safe Output**
- Pydantic schemas for all components
- Structured, validated output
- JSON-serializable results

✅ **Reference Detection**
- Variable references (`var.*`)
- Module outputs (`module.*`)
- Resource attributes (`resource.name.attr`)
- Local values (`local.*`)
- Data sources (`data.*`)

✅ **Modular Architecture**
- Separate parser, utilities, and schemas
- Configurable behavior
- Unit-testable design

## Architecture

### Components

1. **TerraformParser** ([`backend/parser/terraform_parser_v2.py`](backend/parser/terraform_parser_v2.py))
   - Main parser class
   - File discovery and parsing
   - Component extraction
   - Repository-level aggregation

2. **Parser Schemas** ([`backend/parser/parser_schemas.py`](backend/parser/parser_schemas.py))
   - Pydantic models for all components
   - Type-safe data structures
   - Validation and serialization

3. **Parser Utilities** ([`backend/parser/parser_utils.py`](backend/parser/parser_utils.py))
   - Helper functions
   - Value normalization
   - Reference detection
   - Provider extraction

## Installation

The parser requires `python-hcl2`:

```bash
pip install python-hcl2==4.3.2
```

## Usage

### Basic Usage

```python
from parser.terraform_parser_v2 import TerraformParser

# Initialize parser
parser = TerraformParser()

# Parse repository
result = parser.parse_repository("/path/to/terraform/repo")

# Access parsed components
print(f"Found {len(result.resources)} resources")
print(f"Found {len(result.modules)} modules")
print(f"Found {len(result.variables)} variables")

# Get formatted output
output = parser.format_output(result)
```

### With Configuration

```python
from parser.terraform_parser_v2 import TerraformParser
from parser.parser_schemas import ParserConfig

# Custom configuration
config = ParserConfig(
    exclude_dirs=['.terraform', '.git', 'custom_dir'],
    max_file_size_mb=10,
    continue_on_error=True,
    extract_references=True
)

parser = TerraformParser(config=config)
result = parser.parse_repository("/path/to/repo")
```

### Parse Single File

```python
parser = TerraformParser()

# Parse single file
file_result = parser.parse_file(
    "/path/to/main.tf",
    repo_root="/path/to/repo"
)

# Access components
for resource in file_result.resources:
    print(f"Resource: {resource.full_name}")
    print(f"Provider: {resource.provider}")
    print(f"Metadata: {resource.metadata}")
```

## Output Format

### Repository Parse Result

```python
{
    "status": "success",  # or "partial", "error"
    "total_files": 10,
    "parsed_files": 9,
    "failed_files": 1,
    
    "resources": [
        {
            "type": "aws_vpc",
            "name": "main",
            "full_name": "aws_vpc.main",
            "provider": "aws",
            "metadata": {
                "cidr_block": "10.0.0.0/16",
                "tags": {"Name": "main-vpc"}
            },
            "file_path": "main.tf",
            "line_number": 10
        }
    ],
    
    "modules": [
        {
            "name": "vpc",
            "source": "./modules/vpc",
            "version": "1.0.0",
            "metadata": {"vpc_cidr": "10.0.0.0/16"},
            "file_path": "main.tf",
            "line_number": 25
        }
    ],
    
    "variables": [
        {
            "name": "vpc_cidr",
            "type": "string",
            "default_value": "10.0.0.0/16",
            "description": "VPC CIDR block",
            "sensitive": false,
            "validation": null,
            "metadata": {},
            "file_path": "variables.tf",
            "line_number": 1
        }
    ],
    
    "outputs": [
        {
            "name": "vpc_id",
            "value": "aws_vpc.main.id",
            "description": "VPC ID",
            "sensitive": false,
            "depends_on": [],
            "metadata": {},
            "file_path": "outputs.tf",
            "line_number": 1
        }
    ],
    
    "providers": [
        {
            "name": "aws",
            "version": "~> 5.0",
            "alias": null,
            "source": "hashicorp/aws",
            "metadata": {},
            "file_path": "provider.tf",
            "line_number": 5
        }
    ],
    
    "locals": [
        {
            "name": "common_tags",
            "value": {"Environment": "dev"},
            "file_path": "locals.tf",
            "line_number": 2
        }
    ],
    
    "data_sources": [
        {
            "type": "aws_ami",
            "name": "amazon_linux",
            "full_name": "data.aws_ami.amazon_linux",
            "provider": "aws",
            "metadata": {"most_recent": true},
            "file_path": "data.tf",
            "line_number": 1
        }
    ],
    
    "statistics": {
        "total_resources": 5,
        "total_modules": 2,
        "total_variables": 3,
        "total_outputs": 2,
        "total_providers": 1,
        "total_locals": 2,
        "total_data_sources": 1,
        "total_references": 15
    },
    
    "errors": [
        "main.tf: HCL2 parse error: ..."
    ]
}
```

## Parsed Components

### Resources

```python
ParsedResource(
    type="aws_vpc",
    name="main",
    full_name="aws_vpc.main",
    provider="aws",
    metadata={"cidr_block": "10.0.0.0/16"},
    file_path="main.tf",
    line_number=10
)
```

### Modules

```python
ParsedModule(
    name="vpc",
    source="./modules/vpc",
    version="1.0.0",
    metadata={"vpc_cidr": "10.0.0.0/16"},
    file_path="main.tf",
    line_number=25
)
```

### Variables

```python
ParsedVariable(
    name="vpc_cidr",
    type="string",
    default_value="10.0.0.0/16",
    description="VPC CIDR block",
    sensitive=False,
    validation=None,
    metadata={},
    file_path="variables.tf",
    line_number=1
)
```

### Outputs

```python
ParsedOutput(
    name="vpc_id",
    value="aws_vpc.main.id",
    description="VPC ID",
    sensitive=False,
    depends_on=[],
    metadata={},
    file_path="outputs.tf",
    line_number=1
)
```

### Providers

```python
ParsedProvider(
    name="aws",
    version="~> 5.0",
    alias=None,
    source="hashicorp/aws",
    metadata={},
    file_path="provider.tf",
    line_number=5
)
```

### Local Values

```python
ParsedLocal(
    name="common_tags",
    value={"Environment": "dev", "Project": "test"},
    file_path="locals.tf",
    line_number=2
)
```

### Data Sources

```python
ParsedDataSource(
    type="aws_ami",
    name="amazon_linux",
    full_name="data.aws_ami.amazon_linux",
    provider="aws",
    metadata={"most_recent": True},
    file_path="data.tf",
    line_number=1
)
```

## Configuration Options

### ParserConfig

```python
ParserConfig(
    exclude_dirs=['.terraform', '.git', 'node_modules'],
    file_extensions=['.tf', '.tfvars'],
    max_file_size_mb=10,
    continue_on_error=True,
    extract_references=True,
    normalize_values=True
)
```

**Parameters:**
- `exclude_dirs`: Directories to skip during scanning
- `file_extensions`: File extensions to parse
- `max_file_size_mb`: Maximum file size to parse (MB)
- `continue_on_error`: Continue parsing on file errors
- `extract_references`: Extract variable/resource references
- `normalize_values`: Normalize parsed values to JSON-compatible format

## Error Handling

### Parse Status

- **success**: All files parsed successfully
- **partial**: Some files parsed, some failed
- **error**: No files parsed or critical error

### Error Information

```python
result = parser.parse_repository("/path/to/repo")

if result.status != "success":
    print(f"Status: {result.status}")
    print(f"Parsed: {result.parsed_files}/{result.total_files}")
    print(f"Failed: {result.failed_files}")
    
    for error in result.errors:
        print(f"Error: {error}")
```

### Malformed File Handling

The parser gracefully handles malformed files:

```python
# File with syntax error
bad_tf = """
resource "aws_vpc" "main" {
  cidr_block = "10.0.0.0/16"
  # Missing closing brace
"""

# Parser will:
# 1. Log the error
# 2. Mark file as failed
# 3. Continue with other files (if continue_on_error=True)
# 4. Include error in result.errors
```

## Reference Detection

The parser detects various types of references:

### Variable References

```hcl
resource "aws_vpc" "main" {
  cidr_block = var.vpc_cidr  # Detected
  tags = {
    Name = var.project_name  # Detected
  }
}
```

### Module References

```hcl
resource "aws_subnet" "main" {
  vpc_id = module.vpc.vpc_id  # Detected
  cidr_block = module.network.subnet_cidr  # Detected
}
```

### Resource References

```hcl
resource "aws_subnet" "main" {
  vpc_id = aws_vpc.main.id  # Detected
  security_group_ids = [aws_security_group.main.id]  # Detected
}
```

### Local References

```hcl
resource "aws_vpc" "main" {
  tags = local.common_tags  # Detected
}
```

### Data Source References

```hcl
resource "aws_instance" "main" {
  ami = data.aws_ami.amazon_linux.id  # Detected
}
```

## Utility Functions

### Value Normalization

```python
from parser.parser_utils import normalize_value

# Normalize complex values
normalized = normalize_value({
    "list": [1, 2, 3],
    "dict": {"key": "value"},
    "nested": [{"a": 1}, {"b": 2}]
})
```

### Provider Extraction

```python
from parser.parser_utils import extract_provider_from_resource_type

provider = extract_provider_from_resource_type("aws_vpc")  # "aws"
provider = extract_provider_from_resource_type("azurerm_virtual_network")  # "azurerm"
```

### Reference Detection

```python
from parser.parser_utils import detect_all_references

content = """
resource "aws_subnet" "main" {
  vpc_id = module.vpc.vpc_id
  cidr_block = var.subnet_cidr
}
"""

references = detect_all_references(content)
# Returns list of all detected references
```

## Testing

Run the test suite:

```bash
# Run all parser tests
pytest backend/tests/test_terraform_parser.py -v

# Run specific test
pytest backend/tests/test_terraform_parser.py::TestTerraformParser::test_parse_resources -v

# Run with coverage
pytest backend/tests/test_terraform_parser.py --cov=backend/parser --cov-report=html
```

## Integration Example

### With Repository Ingestion

```python
from services.repo_ingestion_service import RepoIngestionService
from parser.terraform_parser_v2 import TerraformParser

# 1. Ingest repository
ingestion_service = RepoIngestionService()
metadata = ingestion_service.clone_repository(
    "https://github.com/terraform-aws-modules/terraform-aws-vpc"
)

# 2. Parse Terraform files
parser = TerraformParser()
result = parser.parse_repository(metadata['local_path'])

# 3. Use parsed data
print(f"Found {result.statistics['total_resources']} resources")
for resource in result.resources:
    print(f"  - {resource.full_name} ({resource.provider})")
```

### With Database Storage

```python
from parser.terraform_parser_v2 import TerraformParser
from models.models import Repository, Resource, Module
from sqlalchemy.orm import Session

def store_parsed_data(repo_id: int, parse_result, db: Session):
    """Store parsed Terraform data in database"""
    
    # Store resources
    for resource in parse_result.resources:
        db_resource = Resource(
            repository_id=repo_id,
            type=resource.type,
            name=resource.name,
            full_name=resource.full_name,
            provider=resource.provider,
            metadata=resource.metadata
        )
        db.add(db_resource)
    
    # Store modules
    for module in parse_result.modules:
        db_module = Module(
            repository_id=repo_id,
            name=module.name,
            source=module.source,
            version=module.version,
            metadata=module.metadata
        )
        db.add(db_module)
    
    db.commit()
```

## Performance Considerations

### File Size Limits

Large files are skipped by default:

```python
config = ParserConfig(max_file_size_mb=10)
parser = TerraformParser(config=config)
```

### Excluded Directories

Exclude unnecessary directories for faster scanning:

```python
config = ParserConfig(
    exclude_dirs=[
        '.terraform',
        '.git',
        'node_modules',
        '.venv',
        '__pycache__',
        'custom_large_dir'
    ]
)
```

### Continue on Error

Enable to parse as many files as possible:

```python
config = ParserConfig(continue_on_error=True)
parser = TerraformParser(config=config)
```

## Troubleshooting

### Common Issues

**Issue**: `ImportError: No module named 'hcl2'`
- **Solution**: Install python-hcl2: `pip install python-hcl2`

**Issue**: Parse errors on valid Terraform files
- **Solution**: Ensure using HCL2 syntax (Terraform 0.12+)

**Issue**: Missing components in output
- **Solution**: Check file was parsed successfully in `file_results`

**Issue**: Large memory usage
- **Solution**: Reduce `max_file_size_mb` or exclude large directories

## Best Practices

1. **Always check parse status**
   ```python
   result = parser.parse_repository(repo_path)
   if result.status == "error":
       handle_error(result.errors)
   ```

2. **Use configuration for large repositories**
   ```python
   config = ParserConfig(
       max_file_size_mb=5,
       continue_on_error=True
   )
   ```

3. **Handle partial results**
   ```python
   if result.status == "partial":
       logger.warning(f"Parsed {result.parsed_files}/{result.total_files} files")
       # Still use successfully parsed data
   ```

4. **Validate output before use**
   ```python
   if result.resources:
       for resource in result.resources:
           validate_resource(resource)
   ```

## Related Documentation

- [`backend/parser/terraform_parser_v2.py`](backend/parser/terraform_parser_v2.py) - Main parser implementation
- [`backend/parser/parser_schemas.py`](backend/parser/parser_schemas.py) - Type schemas
- [`backend/parser/parser_utils.py`](backend/parser/parser_utils.py) - Utility functions
- [`backend/tests/test_terraform_parser.py`](backend/tests/test_terraform_parser.py) - Test suite

## License

Part of the Infra Knowledge Graph project.