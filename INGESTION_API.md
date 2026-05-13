# Repository Ingestion API Documentation

## Overview

The Repository Ingestion Service provides a comprehensive API for ingesting GitHub repositories, validating URLs, scanning Terraform files, and managing local repository storage.

## Base URL

```
/api/ingestion
```

## Endpoints

### 1. Ingest Repository

Clone a GitHub repository locally and extract metadata.

**Endpoint:** `POST /api/ingestion/ingest`

**Request Body:**
```json
{
  "url": "https://github.com/terraform-aws-modules/terraform-aws-vpc",
  "branch": "main",
  "force_refresh": false
}
```

**Parameters:**
- `url` (required): GitHub repository URL (HTTPS or SSH format)
- `branch` (optional): Git branch to clone (default: "main")
- `force_refresh` (optional): Force re-clone if repository exists (default: false)

**Response:** `201 Created`
```json
{
  "owner": "terraform-aws-modules",
  "name": "terraform-aws-vpc",
  "url": "https://github.com/terraform-aws-modules/terraform-aws-vpc",
  "local_path": "./cloned_repos/terraform-aws-modules/terraform-aws-vpc",
  "branch": "main",
  "commit_hash": "a1b2c3d4",
  "commit_message": "Update VPC module",
  "commit_author": "John Doe <john@example.com>",
  "commit_date": "2024-01-15T10:30:00+00:00",
  "total_commits": 150,
  "is_cloned": true
}
```

**Error Responses:**
- `400 Bad Request`: Invalid GitHub URL format
- `500 Internal Server Error`: Failed to clone repository

---

### 2. Validate Repository URL

Validate a GitHub repository URL without cloning.

**Endpoint:** `POST /api/ingestion/validate`

**Query Parameters:**
- `url` (required): GitHub repository URL to validate

**Example:**
```
POST /api/ingestion/validate?url=https://github.com/hashicorp/terraform
```

**Response:** `200 OK`
```json
{
  "valid": true,
  "owner": "hashicorp",
  "name": "terraform",
  "url": "https://github.com/hashicorp/terraform"
}
```

**Error Response:** `400 Bad Request`
```json
{
  "detail": "Invalid GitHub URL format: ..."
}
```

---

### 3. Get Terraform Files

List all Terraform files in a cloned repository.

**Endpoint:** `GET /api/ingestion/terraform-files/{owner}/{repo}`

**Path Parameters:**
- `owner`: Repository owner
- `repo`: Repository name

**Example:**
```
GET /api/ingestion/terraform-files/terraform-aws-modules/terraform-aws-vpc
```

**Response:** `200 OK`
```json
{
  "owner": "terraform-aws-modules",
  "name": "terraform-aws-vpc",
  "terraform_files": [
    "main.tf",
    "variables.tf",
    "outputs.tf",
    "modules/vpc/main.tf",
    "modules/subnets/main.tf"
  ],
  "total_files": 5
}
```

**Error Responses:**
- `404 Not Found`: Repository not cloned locally
- `500 Internal Server Error`: Failed to scan files

---

### 4. Get Terraform File Content

Retrieve content of a specific Terraform file.

**Endpoint:** `GET /api/ingestion/terraform-files/{owner}/{repo}/{file_path}`

**Path Parameters:**
- `owner`: Repository owner
- `repo`: Repository name
- `file_path`: Relative path to the Terraform file

**Example:**
```
GET /api/ingestion/terraform-files/terraform-aws-modules/terraform-aws-vpc/main.tf
```

**Response:** `200 OK`
```json
{
  "file_path": "main.tf",
  "content": "resource \"aws_vpc\" \"main\" {\n  cidr_block = var.cidr_block\n  ...\n}"
}
```

**Error Response:** `404 Not Found`
```json
{
  "detail": "File not found: main.tf"
}
```

---

### 5. Check Repository Exists

Check if a repository is already cloned locally.

**Endpoint:** `GET /api/ingestion/{owner}/{repo}/exists`

**Path Parameters:**
- `owner`: Repository owner
- `repo`: Repository name

**Example:**
```
GET /api/ingestion/terraform-aws-modules/terraform-aws-vpc/exists
```

**Response:** `200 OK`
```json
{
  "exists": true,
  "owner": "terraform-aws-modules",
  "name": "terraform-aws-vpc"
}
```

---

### 6. Delete Repository

Delete a cloned repository from local storage.

**Endpoint:** `DELETE /api/ingestion/{owner}/{repo}`

**Path Parameters:**
- `owner`: Repository owner
- `repo`: Repository name

**Example:**
```
DELETE /api/ingestion/terraform-aws-modules/terraform-aws-vpc
```

**Response:** `200 OK`
```json
{
  "success": true,
  "message": "Repository terraform-aws-modules/terraform-aws-vpc deleted successfully"
}
```

**Error Responses:**
- `404 Not Found`: Repository not found
- `500 Internal Server Error`: Failed to delete repository

---

### 7. Get Storage Usage

Get storage usage statistics for all cloned repositories.

**Endpoint:** `GET /api/ingestion/storage`

**Response:** `200 OK`
```json
{
  "total_bytes": 52428800,
  "total_mb": 50.0,
  "repositories": 3
}
```

---

### 8. Cleanup Old Repositories

Clean up repositories older than specified age.

**Endpoint:** `POST /api/ingestion/cleanup`

**Query Parameters:**
- `max_age_days` (optional): Maximum age in days (default: 30)

**Example:**
```
POST /api/ingestion/cleanup?max_age_days=30
```

**Response:** `200 OK`
```json
{
  "checked": 10,
  "deleted": 3,
  "errors": 0
}
```

---

## Supported URL Formats

The service supports the following GitHub URL formats:

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

---

## Error Handling

All endpoints return appropriate HTTP status codes and error messages:

- `400 Bad Request`: Invalid input or validation error
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server-side error

Error response format:
```json
{
  "detail": "Error message describing what went wrong"
}
```

---

## Usage Examples

### Example 1: Ingest and Scan Repository

```bash
# 1. Ingest repository
curl -X POST "http://localhost:8000/api/ingestion/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://github.com/terraform-aws-modules/terraform-aws-vpc",
    "branch": "main"
  }'

# 2. List Terraform files
curl "http://localhost:8000/api/ingestion/terraform-files/terraform-aws-modules/terraform-aws-vpc"

# 3. Get file content
curl "http://localhost:8000/api/ingestion/terraform-files/terraform-aws-modules/terraform-aws-vpc/main.tf"
```

### Example 2: Validate Before Ingesting

```bash
# 1. Validate URL first
curl -X POST "http://localhost:8000/api/ingestion/validate?url=https://github.com/hashicorp/terraform"

# 2. If valid, ingest
curl -X POST "http://localhost:8000/api/ingestion/ingest" \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://github.com/hashicorp/terraform"
  }'
```

### Example 3: Cleanup and Storage Management

```bash
# 1. Check storage usage
curl "http://localhost:8000/api/ingestion/storage"

# 2. Cleanup old repositories
curl -X POST "http://localhost:8000/api/ingestion/cleanup?max_age_days=30"

# 3. Delete specific repository
curl -X DELETE "http://localhost:8000/api/ingestion/terraform-aws-modules/terraform-aws-vpc"
```

---

## Service Features

### URL Validation
- Validates GitHub URL format (HTTPS and SSH)
- Extracts owner and repository name
- Normalizes URLs to HTTPS format
- Supports public repositories only

### Repository Cloning
- Uses GitPython for reliable cloning
- Shallow cloning (depth=1) for efficiency
- Automatic update of existing repositories
- Force refresh option for re-cloning

### Terraform File Scanning
- Recursively scans all `.tf` and `.tfvars` files
- Excludes `.terraform`, `.git`, and other non-relevant directories
- Returns relative file paths for easy reference
- Secure file reading with path traversal protection

### Storage Management
- Track storage usage across all repositories
- Cleanup old repositories by age
- Delete individual repositories
- Calculate total storage in bytes and MB

### Error Handling
- Custom exceptions for validation and ingestion errors
- Comprehensive error messages
- Proper HTTP status codes
- Logging for debugging and monitoring

---

## Configuration

The service uses the following configuration from `backend/config/settings.py`:

```python
tf_workspace_dir: str = "./cloned_repos"  # Local storage directory
max_repo_size_mb: int = 500               # Maximum repository size
```

These can be overridden via environment variables:
```bash
TF_WORKSPACE_DIR=./my_repos
MAX_REPO_SIZE_MB=1000
```

---

## Security Considerations

1. **Public Repositories Only**: The service only supports public GitHub repositories
2. **Path Traversal Protection**: File reading includes path validation to prevent directory traversal attacks
3. **URL Validation**: Strict validation of GitHub URLs before cloning
4. **Storage Limits**: Configurable maximum repository size to prevent disk exhaustion
5. **Cleanup Utilities**: Automatic cleanup of old repositories to manage storage

---

## Integration with Analysis Service

The ingestion service integrates with the analysis service for complete workflow:

```bash
# 1. Ingest repository
POST /api/ingestion/ingest
  → Returns repository metadata

# 2. Analyze repository (uses ingested data)
POST /api/analysis/analyze
  → Parses Terraform files
  → Builds dependency graph
  → Stores in database

# 3. Query results
GET /api/repositories/{id}
GET /api/graphs/{id}
```

---

## Testing

Run the test suite:

```bash
# Unit tests
pytest backend/tests/test_ingestion.py -v

# API integration tests
pytest backend/tests/test_ingestion_api.py -v

# All tests
pytest backend/tests/ -v
```

---

## Logging

The service logs all operations:

```python
logger.info(f"Ingesting repository: {url}")
logger.info(f"Successfully cloned: {owner}/{name}")
logger.error(f"Failed to clone repository: {error}")
```

Logs are written to `logs/app.log` and console output.