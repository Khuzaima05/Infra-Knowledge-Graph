# GitHub Repository Ingestion Service

## Overview

The GitHub Repository Ingestion Service is a comprehensive solution for cloning, validating, and managing GitHub repositories containing Terraform infrastructure code. It provides a robust API for repository ingestion with built-in error handling, storage management, and Terraform file scanning capabilities.

## Features

✅ **GitHub Repository Cloning**
- Clone public GitHub repositories using HTTPS or SSH URLs
- Shallow cloning for efficient bandwidth usage
- Automatic repository updates for existing clones
- Force refresh option for re-cloning

✅ **URL Validation**
- Validate GitHub URLs before cloning
- Support for HTTPS and SSH formats
- Extract owner and repository information
- Normalize URLs to standard format

✅ **Terraform File Scanning**
- Recursively scan all `.tf` and `.tfvars` files
- Exclude irrelevant directories (`.terraform`, `.git`, etc.)
- Return relative file paths
- Read file contents with security protections

✅ **Storage Management**
- Track total storage usage
- Cleanup old repositories by age
- Delete individual repositories
- Calculate storage statistics

✅ **Error Handling**
- Custom exceptions for validation and ingestion errors
- Comprehensive error messages
- Proper HTTP status codes
- Detailed logging

## Architecture

### Components

1. **RepoIngestionService** (`backend/services/repo_ingestion_service.py`)
   - Core service class handling all repository operations
   - URL validation and parsing
   - Repository cloning using GitPython
   - Terraform file scanning
   - Storage management and cleanup

2. **API Routes** (`backend/app/routes/ingestion.py`)
   - FastAPI endpoints for all ingestion operations
   - Request/response validation using Pydantic
   - Error handling and HTTP status codes

3. **Schemas** (`backend/app/schemas.py`)
   - `RepoIngestionRequest`: Request model for ingestion
   - `RepoMetadataResponse`: Repository metadata response
   - `TerraformFilesResponse`: Terraform files listing
   - `StorageUsageResponse`: Storage statistics
   - `CleanupStatsResponse`: Cleanup operation results

4. **Utilities** (`backend/services/repo_utils.py`)
   - Helper functions for validation
   - Storage quota management
   - Repository indexing
   - Directory size calculations

## Installation

### Prerequisites

- Python 3.9+
- Git installed on system
- PostgreSQL database (for full application)

### Dependencies

```bash
pip install -r backend/requirements.txt
```

Key dependencies:
- `GitPython==3.1.40` - Git operations
- `fastapi==0.104.1` - API framework
- `pydantic==2.5.0` - Data validation

## Configuration

Configure via environment variables or `backend/config/settings.py`:

```python
# Repository storage
TF_WORKSPACE_DIR="./cloned_repos"  # Local storage directory
MAX_REPO_SIZE_MB=500               # Maximum repository size

# Application
DATABASE_URL="postgresql://user:pass@localhost:5432/db"
LOG_LEVEL="INFO"
```

## API Endpoints

### Base URL: `/api/ingestion`

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/ingest` | Clone and ingest a repository |
| POST | `/validate` | Validate GitHub URL |
| GET | `/terraform-files/{owner}/{repo}` | List Terraform files |
| GET | `/terraform-files/{owner}/{repo}/{path}` | Get file content |
| GET | `/{owner}/{repo}/exists` | Check if repository exists |
| DELETE | `/{owner}/{repo}` | Delete repository |
| GET | `/storage` | Get storage usage |
| POST | `/cleanup` | Cleanup old repositories |

See [`INGESTION_API.md`](./INGESTION_API.md) for detailed API documentation.

## Usage Examples

### 1. Ingest a Repository

```python
import requests

response = requests.post(
    "http://localhost:8000/api/ingestion/ingest",
    json={
        "url": "https://github.com/terraform-aws-modules/terraform-aws-vpc",
        "branch": "main",
        "force_refresh": False
    }
)

metadata = response.json()
print(f"Cloned: {metadata['owner']}/{metadata['name']}")
print(f"Commit: {metadata['commit_hash']}")
print(f"Files at: {metadata['local_path']}")
```

### 2. Scan Terraform Files

```python
owner = "terraform-aws-modules"
repo = "terraform-aws-vpc"

response = requests.get(
    f"http://localhost:8000/api/ingestion/terraform-files/{owner}/{repo}"
)

files = response.json()
print(f"Found {files['total_files']} Terraform files:")
for file_path in files['terraform_files']:
    print(f"  - {file_path}")
```

### 3. Read File Content

```python
response = requests.get(
    f"http://localhost:8000/api/ingestion/terraform-files/{owner}/{repo}/main.tf"
)

file_data = response.json()
print(f"File: {file_data['file_path']}")
print(f"Content:\n{file_data['content']}")
```

### 4. Manage Storage

```python
# Check storage usage
response = requests.get("http://localhost:8000/api/ingestion/storage")
usage = response.json()
print(f"Storage: {usage['total_mb']} MB across {usage['repositories']} repos")

# Cleanup old repositories (>30 days)
response = requests.post(
    "http://localhost:8000/api/ingestion/cleanup",
    params={"max_age_days": 30}
)
stats = response.json()
print(f"Cleaned up {stats['deleted']} repositories")
```

## Service Class Usage

You can also use the service class directly:

```python
from services.repo_ingestion_service import RepoIngestionService

# Initialize service
service = RepoIngestionService(workspace_dir="./cloned_repos")

# Validate URL
is_valid = service.validate_github_url("https://github.com/owner/repo")

# Parse URL
repo_info = service.parse_github_url("https://github.com/owner/repo")
print(f"Owner: {repo_info['owner']}, Name: {repo_info['name']}")

# Clone repository
metadata = service.clone_repository(
    url="https://github.com/terraform-aws-modules/terraform-aws-vpc",
    branch="main"
)

# Find Terraform files
tf_files = service.find_terraform_files("terraform-aws-modules", "terraform-aws-vpc")

# Read file content
path, content = service.get_terraform_file_content(
    "terraform-aws-modules",
    "terraform-aws-vpc",
    "main.tf"
)

# Cleanup
service.delete_repository("terraform-aws-modules", "terraform-aws-vpc")
```

## Supported URL Formats

### HTTPS URLs
```
https://github.com/owner/repo
https://github.com/owner/repo.git
https://github.com/owner/repo/
```

### SSH URLs
```
git@github.com:owner/repo
git@github.com:owner/repo.git
```

## Error Handling

The service uses custom exceptions:

- `RepositoryValidationError`: Invalid URL or validation failure
- `RepositoryIngestionError`: Cloning or file operation failure

Example error handling:

```python
from services.repo_ingestion_service import (
    RepoIngestionService,
    RepositoryValidationError,
    RepositoryIngestionError
)

try:
    service = RepoIngestionService()
    metadata = service.clone_repository("https://github.com/owner/repo")
except RepositoryValidationError as e:
    print(f"Invalid URL: {e}")
except RepositoryIngestionError as e:
    print(f"Failed to clone: {e}")
```

## Testing

### Run Unit Tests

```bash
# Test service functionality
pytest backend/tests/test_ingestion.py -v

# Test API endpoints
pytest backend/tests/test_ingestion_api.py -v

# Run all tests with coverage
pytest backend/tests/ -v --cov=backend/services --cov=backend/app/routes
```

### Test Coverage

The test suite includes:
- URL validation tests (HTTPS, SSH, invalid formats)
- URL parsing tests
- Repository cloning tests
- Terraform file scanning tests
- File content reading tests
- Storage management tests
- Cleanup operation tests
- API endpoint tests
- Full workflow integration tests

## Security Considerations

1. **Public Repositories Only**: Only supports public GitHub repositories
2. **Path Traversal Protection**: Validates file paths to prevent directory traversal
3. **URL Validation**: Strict GitHub URL format validation
4. **Storage Limits**: Configurable maximum repository size
5. **Secure File Reading**: Uses safe file reading with error handling

## Performance Optimization

- **Shallow Cloning**: Uses `depth=1` for faster cloning
- **Single Branch**: Clones only the specified branch
- **Excluded Directories**: Skips `.terraform`, `.git`, `node_modules`
- **Efficient Scanning**: Uses `os.walk` with directory filtering

## Logging

All operations are logged for debugging and monitoring:

```python
logger.info(f"Cloning repository from {url}")
logger.info(f"Successfully cloned: {owner}/{name}")
logger.error(f"Failed to clone repository: {error}")
logger.warning(f"Repository already exists, updating: {path}")
```

Logs are written to:
- Console output (stdout)
- Log file: `logs/app.log`

## Integration with Analysis Service

The ingestion service integrates seamlessly with the analysis service:

```
1. Ingest Repository
   ↓
2. Scan Terraform Files
   ↓
3. Parse Terraform Code
   ↓
4. Build Dependency Graph
   ↓
5. Store in Database
```

Example workflow:

```python
# 1. Ingest
metadata = ingestion_service.clone_repository(url)

# 2. Analyze
from services.analysis_service import AnalysisService
analysis_service = AnalysisService(db)
repo = analysis_service.analyze_repository(url, branch)

# 3. Query
from services.analysis_service import RepositoryService
repo_service = RepositoryService(db)
repo_data = repo_service.get_repository(repo.id)
```

## Troubleshooting

### Common Issues

**Issue**: `GitCommandError: Authentication failed`
- **Solution**: Ensure repository is public or configure SSH keys

**Issue**: `RepositoryIngestionError: Failed to clone`
- **Solution**: Check network connectivity and repository URL

**Issue**: `RepositoryValidationError: Invalid GitHub URL`
- **Solution**: Verify URL format matches supported patterns

**Issue**: Storage quota exceeded
- **Solution**: Run cleanup or increase `MAX_REPO_SIZE_MB`

## Contributing

When contributing to the ingestion service:

1. Add tests for new functionality
2. Update API documentation
3. Follow existing code patterns
4. Add logging for important operations
5. Handle errors appropriately

## License

Part of the Infra Knowledge Graph project.

## Related Documentation

- [`INGESTION_API.md`](./INGESTION_API.md) - Detailed API documentation
- [`API.md`](./API.md) - Complete API reference
- [`ARCHITECTURE.md`](./ARCHITECTURE.md) - System architecture
- [`DEVELOPMENT.md`](./DEVELOPMENT.md) - Development guide