# Quick Start: Repository Analysis

Get started with the complete repository analysis workflow in 5 minutes.

## Prerequisites

- Docker and Docker Compose installed
- Git installed
- Python 3.11+ (for local development)

## Quick Start

### 1. Start the Services

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps
```

Services will be available at:
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Frontend**: http://localhost:3000
- **PostgreSQL**: localhost:5432

### 2. Analyze Your First Repository

#### Using cURL

```bash
# Start analysis (async mode)
curl -X POST http://localhost:8000/api/v1/analysis/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://github.com/terraform-aws-modules/terraform-aws-vpc",
    "branch": "main",
    "async_mode": true
  }'

# Response:
# {
#   "repository_id": 1,
#   "status": "analyzing",
#   "message": "Analysis started for terraform-aws-vpc",
#   "analysis_started": true,
#   "estimated_time_seconds": 60
# }
```

#### Using Python

```python
import requests
import time

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
print(f"Analysis started for repository {repo_id}")

# Poll for completion
while True:
    status = requests.get(
        f"http://localhost:8000/api/v1/analysis/status/{repo_id}"
    ).json()
    
    print(f"Status: {status['status']}")
    
    if status['status'] in ['completed', 'failed']:
        break
    
    time.sleep(5)

# Get results
if status['status'] == 'completed':
    print(f"Analysis completed!")
    print(f"Resources: {status['statistics']['total_resources']}")
    print(f"Modules: {status['statistics']['total_modules']}")
```

### 3. Check Analysis Status

```bash
# Get status
curl http://localhost:8000/api/v1/analysis/status/1

# Response:
# {
#   "id": 1,
#   "name": "terraform-aws-vpc",
#   "url": "https://github.com/terraform-aws-modules/terraform-aws-vpc",
#   "status": "completed",
#   "analyzed_at": "2024-01-15T10:30:00Z",
#   "error_message": null,
#   "statistics": {
#     "total_resources": 45,
#     "total_modules": 3,
#     "total_variables": 12,
#     "total_outputs": 8,
#     "providers_count": 1
#   }
# }
```

### 4. View Results

#### Get Repository Details

```bash
curl http://localhost:8000/api/v1/analysis/repository/1
```

#### Get Dependency Graph

```bash
curl http://localhost:8000/api/v1/graphs/1
```

#### Get Architecture Summary

```bash
curl http://localhost:8000/api/v1/repositories/1/summary
```

### 5. View in Frontend

Open http://localhost:3000 in your browser to:
- View interactive dependency graph
- Explore infrastructure components
- Search and filter resources
- Analyze dependencies

## Common Use Cases

### Analyze Multiple Repositories

```bash
# Repository 1
curl -X POST http://localhost:8000/api/v1/analysis/analyze \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com/terraform-aws-modules/terraform-aws-vpc"}'

# Repository 2
curl -X POST http://localhost:8000/api/v1/analysis/analyze \
  -H "Content-Type: application/json" \
  -d '{"url": "https://github.com/terraform-aws-modules/terraform-aws-eks"}'

# List all repositories
curl http://localhost:8000/api/v1/analysis/repositories
```

### Force Refresh Analysis

```bash
curl -X POST http://localhost:8000/api/v1/analysis/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://github.com/terraform-aws-modules/terraform-aws-vpc",
    "force_refresh": true
  }'
```

### Synchronous Analysis

```bash
# Wait for completion (no background task)
curl -X POST http://localhost:8000/api/v1/analysis/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://github.com/terraform-aws-modules/terraform-aws-vpc",
    "async_mode": false
  }'
```

### Delete Repository

```bash
curl -X DELETE http://localhost:8000/api/v1/analysis/repository/1
```

## API Endpoints Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/analysis/analyze` | Start repository analysis |
| GET | `/api/v1/analysis/status/{id}` | Get analysis status |
| GET | `/api/v1/analysis/repository/{id}` | Get repository details |
| GET | `/api/v1/analysis/repositories` | List all repositories |
| DELETE | `/api/v1/analysis/repository/{id}` | Delete repository |
| GET | `/api/v1/graphs/{id}` | Get dependency graph |
| GET | `/api/v1/repositories/{id}/summary` | Get architecture summary |

## Workflow Overview

```
1. Submit Repository URL
         ↓
2. Clone Repository (GitPython)
         ↓
3. Parse Terraform Files (python-hcl2)
         ↓
4. Resolve References
         ↓
5. Build Dependency Graph (NetworkX)
         ↓
6. Store in Database (PostgreSQL)
         ↓
7. Generate Summary
         ↓
8. Return Results
```

## Troubleshooting

### Analysis Stuck in "analyzing" Status

```bash
# Check logs
docker-compose logs backend

# Restart backend
docker-compose restart backend
```

### Clone Failures

- Verify repository is public
- Check GitHub URL format
- Ensure network connectivity

### Parse Errors

- Check Terraform syntax
- Review parser logs
- Try with simpler repository first

## Next Steps

1. **Explore API Documentation**: http://localhost:8000/docs
2. **Read Full Documentation**: [ANALYSIS_WORKFLOW.md](ANALYSIS_WORKFLOW.md)
3. **View Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)
4. **Run Tests**: `pytest backend/tests/test_analysis_workflow.py -v`

## Example Repositories to Try

Public Terraform repositories perfect for testing:

```bash
# AWS VPC Module
https://github.com/terraform-aws-modules/terraform-aws-vpc

# AWS EKS Module
https://github.com/terraform-aws-modules/terraform-aws-eks

# AWS RDS Module
https://github.com/terraform-aws-modules/terraform-aws-rds

# Azure Network Module
https://github.com/Azure/terraform-azurerm-network

# Google Cloud Network Module
https://github.com/terraform-google-modules/terraform-google-network
```

## Support

- **Documentation**: See [ANALYSIS_WORKFLOW.md](ANALYSIS_WORKFLOW.md)
- **API Reference**: http://localhost:8000/docs
- **Issues**: Check application logs
- **Development**: See [DEVELOPMENT.md](DEVELOPMENT.md)