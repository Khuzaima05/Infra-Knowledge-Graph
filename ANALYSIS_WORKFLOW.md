# Complete Repository Analysis Workflow

Comprehensive documentation for the end-to-end Terraform repository analysis system.

## Overview

The analysis workflow orchestrates multiple services to provide complete infrastructure analysis:

1. **Repository Ingestion** - Clone and validate GitHub repositories
2. **Terraform Parsing** - Extract all infrastructure components
3. **Reference Resolution** - Resolve dependencies between components
4. **Graph Building** - Create dependency graph with statistics
5. **Database Storage** - Persist all metadata and relationships
6. **Summary Generation** - Generate architecture overview

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Analysis Orchestrator                     │
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Ingestion   │→ │   Parser     │→ │    Graph     │      │
│  │   Service    │  │   (v2)       │  │  Builder(v2) │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         ↓                  ↓                  ↓              │
│  ┌──────────────────────────────────────────────────┐      │
│  │            Database (PostgreSQL)                  │      │
│  │  - Repositories  - Resources   - Graph           │      │
│  │  - Files         - Modules     - Summary         │      │
│  └──────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────┘
```

## Components

### 1. Analysis Orchestrator

**File:** `backend/services/analysis_orchestrator.py`

Main orchestration service that coordinates the entire workflow.

**Key Methods:**
- `analyze_repository()` - Synchronous analysis
- `analyze_repository_async()` - Async wrapper for background tasks
- `get_analysis_status()` - Check analysis progress

**Features:**
- Step-by-step workflow execution
- Comprehensive error handling
- Database transaction management
- Status tracking and updates

### 2. Repository Ingestion Service

**File:** `backend/services/repo_ingestion_service.py`

Handles GitHub repository operations.

**Capabilities:**
- URL validation (HTTPS and SSH)
- Repository cloning with GitPython
- Metadata extraction
- Local storage management
- Cleanup utilities

### 3. Terraform Parser (v2)

**File:** `backend/parser/terraform_parser_v2.py`

Enhanced parser using python-hcl2.

**Extracts:**
- Resources with attributes
- Modules with inputs
- Variables with types
- Outputs with values
- Providers with configuration
- Locals and data sources

**Features:**
- Malformed file handling
- Reference detection
- Type inference
- Comprehensive error reporting

### 4. Graph Builder (v2)

**File:** `backend/graph/graph_builder_v2.py`

Builds dependency graphs with advanced analysis.

**Capabilities:**
- Reference resolution
- Dependency edge creation
- Variable lineage tracking
- Statistics computation
- Cycle detection

## API Endpoints

### POST /api/v1/analysis/analyze

Analyze a Terraform repository with complete workflow.

**Request:**
```json
{
  "url": "https://github.com/terraform-aws-modules/terraform-aws-vpc",
  "branch": "main",
  "force_refresh": false,
  "async_mode": true
}
```

**Response (Async Mode):**
```json
{
  "repository_id": 1,
  "status": "analyzing",
  "message": "Analysis started for terraform-aws-vpc",
  "analysis_started": true,
  "estimated_time_seconds": 60
}
```

**Response (Sync Mode):**
```json
{
  "repository_id": 1,
  "status": "completed",
  "message": "Analysis completed for terraform-aws-vpc",
  "analysis_started": true,
  "estimated_time_seconds": 0
}
```

### GET /api/v1/analysis/status/{repo_id}

Get current analysis status.

**Response:**
```json
{
  "id": 1,
  "name": "terraform-aws-vpc",
  "url": "https://github.com/terraform-aws-modules/terraform-aws-vpc",
  "status": "completed",
  "analyzed_at": "2024-01-15T10:30:00Z",
  "error_message": null,
  "statistics": {
    "total_resources": 45,
    "total_modules": 3,
    "total_variables": 12,
    "total_outputs": 8,
    "providers_count": 1
  }
}
```

### GET /api/v1/analysis/repository/{repo_id}

Get complete repository details.

**Response:**
```json
{
  "id": 1,
  "name": "terraform-aws-vpc",
  "url": "https://github.com/terraform-aws-modules/terraform-aws-vpc",
  "branch": "main",
  "status": "completed",
  "statistics": {
    "total_resources": 45,
    "total_modules": 3,
    "total_variables": 12,
    "total_outputs": 8,
    "providers_count": 1
  },
  "analyzed_at": "2024-01-15T10:30:00Z",
  "created_at": "2024-01-15T10:25:00Z"
}
```

### DELETE /api/v1/analysis/repository/{repo_id}

Delete repository analysis and local clone.

**Response:**
```json
{
  "message": "Repository terraform-aws-vpc deleted successfully",
  "repository_id": 1
}
```

### GET /api/v1/analysis/repositories

List all analyzed repositories with pagination.

**Query Parameters:**
- `skip` - Number of records to skip (default: 0)
- `limit` - Maximum records to return (default: 10)
- `status` - Filter by status (optional)

**Response:**
```json
{
  "total": 25,
  "skip": 0,
  "limit": 10,
  "repositories": [
    {
      "id": 1,
      "name": "terraform-aws-vpc",
      "url": "https://github.com/terraform-aws-modules/terraform-aws-vpc",
      "status": "completed",
      "analyzed_at": "2024-01-15T10:30:00Z",
      "statistics": {
        "total_resources": 45,
        "total_modules": 3,
        "total_variables": 12,
        "total_outputs": 8,
        "providers_count": 1
      }
    }
  ]
}
```

## Workflow Steps

### Step 1: URL Validation

```python
repo_info = orchestrator._validate_url(url)
# Returns: {'owner': 'owner', 'name': 'repo', 'url': 'normalized_url'}
```

**Validates:**
- GitHub URL format (HTTPS or SSH)
- Owner and repository names
- URL normalization

### Step 2: Repository Record

```python
repo = orchestrator._get_or_create_repository(url, branch, repo_info)
repo.status = 'analyzing'
```

**Actions:**
- Create new or update existing record
- Set status to 'analyzing'
- Store in database

### Step 3: Clone Repository

```python
clone_metadata = orchestrator._clone_repository(url, branch, force_refresh)
repo.cloned_path = clone_metadata['local_path']
```

**Features:**
- Shallow clone for efficiency
- Update existing clones
- Force refresh option
- Metadata extraction

### Step 4: Parse Terraform Files

```python
parsed_repo = orchestrator._parse_terraform_files(local_path)
```

**Extracts:**
- All .tf and .tfvars files
- Resources, modules, variables
- Outputs, providers, locals
- Data sources

### Step 5: Build Dependency Graph

```python
graph_result = orchestrator._build_graph(parsed_repo)
```

**Creates:**
- Nodes for all components
- Edges for dependencies
- Statistics and metrics
- Reference mappings

### Step 6: Store Metadata

```python
orchestrator._store_terraform_files(repo, local_path, parsed_repo)
orchestrator._store_parsed_components(repo, parsed_repo)
orchestrator._store_graph(repo, graph_result)
```

**Stores:**
- Terraform file contents
- All parsed components
- Graph nodes and edges
- Relationships

### Step 7: Generate Summary

```python
orchestrator._generate_summary(repo, parsed_repo, graph_result)
orchestrator._update_statistics(repo)
```

**Generates:**
- Architecture description
- Key components list
- Deployment overview
- Statistics summary

## Status Values

| Status | Description |
|--------|-------------|
| `pending` | Repository record created, analysis not started |
| `analyzing` | Analysis in progress |
| `completed` | Analysis finished successfully |
| `failed` | Analysis failed with error |

## Error Handling

### Error Types

1. **RepositoryValidationError** - Invalid GitHub URL
2. **RepositoryIngestionError** - Cloning or file access failed
3. **AnalysisError** - General analysis failure

### Error Response

```json
{
  "detail": "Analysis failed: Terraform parsing error in main.tf"
}
```

### Recovery

Failed analyses are marked with:
- `status = 'failed'`
- `error_message` containing details
- `analyzed_at` timestamp

## Background Tasks

### Async Mode

When `async_mode=true`:

1. Create/update repository record
2. Set status to 'analyzing'
3. Return immediately with repository ID
4. Run analysis in background thread
5. Update status on completion/failure

### Monitoring

Poll status endpoint to track progress:

```bash
GET /api/v1/analysis/status/{repo_id}
```

## Database Schema

### Repository Table

```sql
CREATE TABLE repositories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    url VARCHAR(255) UNIQUE NOT NULL,
    branch VARCHAR(255) DEFAULT 'main',
    cloned_path VARCHAR(500),
    total_resources INTEGER DEFAULT 0,
    total_modules INTEGER DEFAULT 0,
    total_variables INTEGER DEFAULT 0,
    total_outputs INTEGER DEFAULT 0,
    providers_count INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'pending',
    error_message TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    analyzed_at TIMESTAMP,
    updated_at TIMESTAMP DEFAULT NOW()
);
```

### Related Tables

- `terraform_files` - File contents
- `modules` - Module definitions
- `resources` - Resource definitions
- `variables` - Variable definitions
- `outputs` - Output definitions
- `providers` - Provider configurations
- `graphs` - Dependency graphs
- `summaries` - Architecture summaries

## Usage Examples

### Python Client

```python
import requests

# Start analysis
response = requests.post(
    "http://localhost:8000/api/v1/analysis/analyze",
    json={
        "url": "https://github.com/terraform-aws-modules/terraform-aws-vpc",
        "branch": "main",
        "async_mode": True
    }
)
repo_id = response.json()["repository_id"]

# Check status
status_response = requests.get(
    f"http://localhost:8000/api/v1/analysis/status/{repo_id}"
)
print(status_response.json())
```

### cURL

```bash
# Start analysis
curl -X POST http://localhost:8000/api/v1/analysis/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://github.com/terraform-aws-modules/terraform-aws-vpc",
    "branch": "main",
    "async_mode": true
  }'

# Check status
curl http://localhost:8000/api/v1/analysis/status/1
```

## Performance Considerations

### Optimization Strategies

1. **Shallow Cloning** - Only fetch latest commit
2. **Async Processing** - Background task execution
3. **Database Indexing** - Fast queries on URLs and status
4. **Caching** - Reuse existing clones when possible

### Resource Usage

- **Memory**: ~100-500MB per analysis
- **Disk**: ~10-50MB per repository
- **Time**: 30-120 seconds typical

## Testing

Run comprehensive tests:

```bash
# Unit tests
pytest backend/tests/test_analysis_workflow.py -v

# Integration tests
pytest backend/tests/test_analysis_workflow.py::TestAnalysisOrchestrator -v

# Specific test
pytest backend/tests/test_analysis_workflow.py::TestAnalysisOrchestrator::test_analyze_repository_success -v
```

## Troubleshooting

### Common Issues

1. **Clone Failures**
   - Check GitHub URL format
   - Verify repository is public
   - Check network connectivity

2. **Parse Errors**
   - Malformed Terraform syntax
   - Unsupported HCL features
   - Check parser logs

3. **Database Errors**
   - Connection issues
   - Schema migrations needed
   - Transaction conflicts

### Debug Mode

Enable detailed logging:

```python
import logging
logging.getLogger('services.analysis_orchestrator').setLevel(logging.DEBUG)
```

## Future Enhancements

- [ ] Private repository support (SSH keys, tokens)
- [ ] Incremental analysis (only changed files)
- [ ] Multi-branch analysis
- [ ] Webhook integration
- [ ] Real-time progress updates (WebSocket)
- [ ] Analysis caching and invalidation
- [ ] Parallel repository processing
- [ ] Custom analysis rules

## Related Documentation

- [Repository Ingestion API](INGESTION_API.md)
- [Terraform Parser](TERRAFORM_PARSER.md)
- [Graph Builder](GRAPH_BUILDER.md)
- [API Documentation](API.md)
- [Architecture Overview](ARCHITECTURE.md)