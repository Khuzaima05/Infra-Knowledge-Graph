# API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication
Currently, no authentication is required. Future versions will support authentication.

## Response Format

All endpoints return JSON responses. Errors follow this format:

```json
{
  "detail": "Error message"
}
```

## Endpoints

### Analysis

#### POST /api/analysis
Analyze a Terraform repository.

**Request:**
```json
{
  "url": "https://github.com/owner/repo",
  "branch": "main"
}
```

**Response (201):**
```json
{
  "id": 1,
  "name": "repo-name",
  "url": "https://github.com/owner/repo",
  "status": "completed",
  "total_resources": 10,
  "total_modules": 2,
  "total_variables": 5,
  "providers_count": 1
}
```

**Status Values:**
- `pending` - Analysis queued
- `analyzing` - Currently analyzing
- `completed` - Analysis finished successfully
- `failed` - Analysis failed

#### GET /api/analysis/{repo_id}/status
Get analysis status for a repository.

**Response:**
```json
{
  "id": 1,
  "status": "completed",
  "analyzed_at": "2024-01-15T10:30:00",
  "error_message": null,
  "statistics": {
    "total_resources": 10,
    "total_modules": 2,
    "total_variables": 5,
    "total_outputs": 3,
    "providers_count": 1
  }
}
```

### Repositories

#### GET /api/repositories
List all analyzed repositories.

**Query Parameters:**
- `skip` (integer, default: 0) - Number of records to skip
- `limit` (integer, default: 10) - Number of records to return

**Response:**
```json
[
  {
    "id": 1,
    "name": "repo-name",
    "url": "https://github.com/owner/repo",
    "status": "completed",
    "total_resources": 10,
    "total_modules": 2,
    "total_variables": 5,
    "providers_count": 1,
    "analyzed_at": "2024-01-15T10:30:00"
  }
]
```

#### GET /api/repositories/{repo_id}
Get detailed repository information.

**Response:**
```json
{
  "id": 1,
  "name": "repo-name",
  "url": "https://github.com/owner/repo",
  "branch": "main",
  "status": "completed",
  "statistics": {
    "total_resources": 10,
    "total_modules": 2,
    "total_variables": 5,
    "total_outputs": 3,
    "providers_count": 1
  },
  "analyzed_at": "2024-01-15T10:30:00",
  "created_at": "2024-01-15T10:00:00"
}
```

#### GET /api/repositories/{repo_id}/modules
Get all modules in a repository.

**Response:**
```json
[
  {
    "id": 1,
    "name": "vpc",
    "source": "terraform-aws-modules/vpc/aws",
    "version": "5.0.0",
    "metadata": {
      "key": "value"
    }
  }
]
```

#### GET /api/repositories/{repo_id}/resources
Get all resources in a repository.

**Response:**
```json
[
  {
    "id": 1,
    "type": "aws_vpc",
    "name": "main",
    "full_name": "aws_vpc.main",
    "provider": "aws",
    "metadata": {
      "cidr_block": "10.0.0.0/16"
    }
  }
]
```

#### GET /api/repositories/{repo_id}/variables
Get all variables in a repository.

**Response:**
```json
[
  {
    "id": 1,
    "name": "vpc_cidr",
    "type": "string",
    "default_value": "10.0.0.0/16",
    "description": "VPC CIDR block"
  }
]
```

#### GET /api/repositories/{repo_id}/providers
Get all providers used in a repository.

**Response:**
```json
[
  {
    "id": 1,
    "name": "aws",
    "version": "~> 5.0",
    "alias": null
  }
]
```

### Graphs

#### GET /api/graphs/{repo_id}/dependency-graph
Get the dependency graph for a repository.

**Response:**
```json
{
  "id": 1,
  "repository_id": 1,
  "nodes": [
    {
      "id": "aws_vpc.main",
      "label": "aws_vpc.main",
      "type": "resource",
      "data": {
        "nodeType": "resource",
        "name": "main",
        "resourceType": "aws_vpc",
        "provider": "aws"
      },
      "metadata": {}
    }
  ],
  "edges": [
    {
      "id": "aws_security_group.main->aws_vpc.main",
      "source": "aws_security_group.main",
      "target": "aws_vpc.main",
      "type": "default",
      "data": {
        "relationshipType": "depends_on"
      }
    }
  ],
  "statistics": {
    "node_count": 10,
    "edge_count": 8,
    "graph_type": "dependency"
  },
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

**Node Types:**
- `resource` - Terraform resource
- `variable` - Terraform variable
- `module` - Terraform module
- `provider` - Cloud provider
- `output` - Terraform output
- `local` - Local value
- `data` - Data source

**Relationship Types:**
- `references` - References another component
- `uses` - Uses a variable or module output
- `uses_provider` - Uses a provider
- `depends_on` - Explicit dependency

#### GET /api/graphs/{repo_id}/summary
Get the architecture summary for a repository.

**Response:**
```json
{
  "id": 1,
  "repository_id": 1,
  "title": "repo-name Infrastructure",
  "architecture_description": "This Terraform infrastructure defines 10 resources across 1 provider(s)...",
  "key_components": [
    {
      "name": "AWS Provider",
      "description": "Manages resources on AWS"
    },
    {
      "name": "Module: vpc",
      "description": "Sourced from terraform-aws-modules/vpc/aws"
    }
  ],
  "deployment_overview": "The infrastructure consists of 1 cloud provider(s) and 2 external module(s)...",
  "created_at": "2024-01-15T10:30:00",
  "updated_at": "2024-01-15T10:30:00"
}
```

## Error Codes

| Code | Description |
|------|-------------|
| 200 | Successful request |
| 201 | Resource created |
| 400 | Bad request (invalid parameters) |
| 404 | Resource not found |
| 500 | Internal server error |
| 503 | Service unavailable |

## Rate Limiting

Currently, no rate limiting is implemented. This may be added in future versions.

## Pagination

Use `skip` and `limit` query parameters:

```
GET /api/repositories?skip=0&limit=10
```

## Sorting

Not currently supported. Will be added in future versions.

## Filtering

Not currently supported. Will be added in future versions.

## Webhooks

Not currently supported. Will be added in future versions.

## Examples

### Analyze a Repository

```bash
curl -X POST http://localhost:8000/api/analysis \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://github.com/terraform-aws-modules/terraform-aws-vpc",
    "branch": "main"
  }'
```

### List Repositories

```bash
curl http://localhost:8000/api/repositories
```

### Get Repository Details

```bash
curl http://localhost:8000/api/repositories/1
```

### Get Dependency Graph

```bash
curl http://localhost:8000/api/graphs/1/dependency-graph
```

### Get Architecture Summary

```bash
curl http://localhost:8000/api/graphs/1/summary
```

## Changelog

### Version 1.0.0
- Initial release
- Basic repository analysis
- Dependency graph generation
- Architecture summaries

## Future Enhancements

- Authentication and authorization
- Webhooks for notifications
- Advanced filtering and search
- Analysis scheduling
- Terraform plan file support
- Cost estimation
- Policy compliance checks
