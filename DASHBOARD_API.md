# Dashboard API Documentation

Comprehensive dashboard endpoints for repository statistics, metadata, and visualization data.

## Overview

The Dashboard API provides three main endpoints for accessing repository analysis results:

1. **GET /dashboard/repo/{id}** - Complete repository dashboard with all statistics
2. **GET /dashboard/summary/{id}** - Architecture summary and key components
3. **GET /dashboard/graph/{id}** - Detailed graph statistics and structure

## Endpoints

### 1. Get Repository Dashboard

**Endpoint:** `GET /api/v1/dashboard/repo/{repo_id}`

Get comprehensive repository dashboard with all statistics and metadata.

#### Response Schema

```json
{
  "id": 1,
  "name": "terraform-aws-vpc",
  "url": "https://github.com/terraform-aws-modules/terraform-aws-vpc",
  "branch": "main",
  "status": "completed",
  "statistics": {
    "resources": 45,
    "modules": 3,
    "variables": 12,
    "outputs": 8,
    "providers": 1,
    "files": 15,
    "dependencies": 67
  },
  "graph_statistics": {
    "total_nodes": 69,
    "total_edges": 67,
    "resource_nodes": 45,
    "module_nodes": 3,
    "variable_nodes": 12,
    "output_nodes": 8,
    "provider_nodes": 1,
    "data_source_nodes": 0,
    "local_nodes": 0
  },
  "metadata": {
    "analyzed_at": "2024-01-15T10:30:00Z",
    "created_at": "2024-01-15T10:25:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "cloned_path": "/path/to/cloned/repo",
    "error_message": null
  }
}
```

#### Statistics Fields

| Field | Type | Description |
|-------|------|-------------|
| `resources` | int | Total number of Terraform resources |
| `modules` | int | Total number of modules |
| `variables` | int | Total number of input variables |
| `outputs` | int | Total number of outputs |
| `providers` | int | Total number of providers |
| `files` | int | Total number of Terraform files |
| `dependencies` | int | Total number of dependency edges in graph |

#### Graph Statistics Fields

| Field | Type | Description |
|-------|------|-------------|
| `total_nodes` | int | Total nodes in dependency graph |
| `total_edges` | int | Total edges (dependencies) |
| `resource_nodes` | int | Number of resource nodes |
| `module_nodes` | int | Number of module nodes |
| `variable_nodes` | int | Number of variable nodes |
| `output_nodes` | int | Number of output nodes |
| `provider_nodes` | int | Number of provider nodes |
| `data_source_nodes` | int | Number of data source nodes |
| `local_nodes` | int | Number of local value nodes |

#### Example Request

```bash
curl http://localhost:8000/api/v1/dashboard/repo/1
```

```python
import requests

response = requests.get("http://localhost:8000/api/v1/dashboard/repo/1")
dashboard = response.json()

print(f"Repository: {dashboard['name']}")
print(f"Resources: {dashboard['statistics']['resources']}")
print(f"Dependencies: {dashboard['statistics']['dependencies']}")
```

---

### 2. Get Repository Summary

**Endpoint:** `GET /api/v1/dashboard/summary/{repo_id}`

Get architecture summary with description and key components.

#### Response Schema

```json
{
  "id": 1,
  "repository_id": 1,
  "title": "terraform-aws-vpc Infrastructure Analysis",
  "architecture_description": "This Terraform infrastructure consists of 45 resources, 3 modules, 12 variables, and 8 outputs across 1 provider(s). The dependency graph contains 69 nodes and 67 edges.",
  "key_components": [
    {
      "name": "aws Provider",
      "description": "Version: ~> 5.0"
    },
    {
      "name": "Module: vpc",
      "description": "Source: terraform-aws-modules/vpc/aws"
    },
    {
      "name": "Module: subnets",
      "description": "Source: ./modules/subnets"
    }
  ],
  "deployment_overview": "The infrastructure uses 1 cloud provider(s) and defines 45 resources. There are 3 reusable modules for modular infrastructure management. The graph analysis identified 67 dependencies between components.",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

#### Fields

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Summary title |
| `architecture_description` | string | High-level architecture overview |
| `key_components` | array | List of important components |
| `deployment_overview` | string | Deployment and usage summary |

#### Example Request

```bash
curl http://localhost:8000/api/v1/dashboard/summary/1
```

```python
import requests

response = requests.get("http://localhost:8000/api/v1/dashboard/summary/1")
summary = response.json()

print(f"Title: {summary['title']}")
print(f"Description: {summary['architecture_description']}")
print(f"Key Components: {len(summary['key_components'])}")
```

---

### 3. Get Graph Statistics

**Endpoint:** `GET /api/v1/dashboard/graph/{repo_id}`

Get detailed graph statistics with complete node and edge data.

#### Response Schema

```json
{
  "id": 1,
  "repository_id": 1,
  "nodes": [
    {
      "id": "resource.aws_vpc.main",
      "type": "resource",
      "label": "aws_vpc.main",
      "data": {
        "type": "aws_vpc",
        "name": "main",
        "provider": "aws"
      },
      "metadata": {}
    }
  ],
  "edges": [
    {
      "id": "edge_1",
      "source": "resource.aws_vpc.main",
      "target": "resource.aws_subnet.public",
      "type": "depends_on",
      "label": "depends on",
      "metadata": {}
    }
  ],
  "statistics": {
    "total_nodes": 69,
    "total_edges": 67,
    "node_types": {
      "resource": 45,
      "module": 3,
      "variable": 12,
      "output": 8,
      "provider": 1
    },
    "edge_types": {
      "depends_on": 30,
      "uses": 25,
      "references": 12
    },
    "complexity_metrics": {
      "average_degree": 1.94,
      "max_degree": 8,
      "density": 0.0282
    }
  },
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

#### Complexity Metrics

| Metric | Description |
|--------|-------------|
| `average_degree` | Average number of connections per node |
| `max_degree` | Maximum connections for any single node |
| `density` | Graph density (actual edges / possible edges) |

#### Example Request

```bash
curl http://localhost:8000/api/v1/dashboard/graph/1
```

```python
import requests

response = requests.get("http://localhost:8000/api/v1/dashboard/graph/1")
graph = response.json()

print(f"Nodes: {graph['statistics']['total_nodes']}")
print(f"Edges: {graph['statistics']['total_edges']}")
print(f"Average Degree: {graph['statistics']['complexity_metrics']['average_degree']}")
print(f"Density: {graph['statistics']['complexity_metrics']['density']}")
```

---

### 4. Get All Repositories Overview

**Endpoint:** `GET /api/v1/dashboard/overview`

Get overview of all repositories with key statistics.

#### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `skip` | int | 0 | Number of records to skip |
| `limit` | int | 10 | Maximum records to return (max: 100) |
| `status` | string | null | Filter by status (pending, analyzing, completed, failed) |

#### Response Schema

```json
[
  {
    "id": 1,
    "name": "terraform-aws-vpc",
    "url": "https://github.com/terraform-aws-modules/terraform-aws-vpc",
    "status": "completed",
    "statistics": {
      "resources": 45,
      "modules": 3,
      "variables": 12,
      "outputs": 8,
      "providers": 1,
      "dependencies": 67
    },
    "analyzed_at": "2024-01-15T10:30:00Z"
  },
  {
    "id": 2,
    "name": "terraform-aws-eks",
    "url": "https://github.com/terraform-aws-modules/terraform-aws-eks",
    "status": "completed",
    "statistics": {
      "resources": 78,
      "modules": 5,
      "variables": 25,
      "outputs": 15,
      "providers": 2,
      "dependencies": 120
    },
    "analyzed_at": "2024-01-15T11:00:00Z"
  }
]
```

#### Example Requests

```bash
# Get first 10 repositories
curl http://localhost:8000/api/v1/dashboard/overview

# Get next 10 repositories
curl http://localhost:8000/api/v1/dashboard/overview?skip=10&limit=10

# Get only completed repositories
curl http://localhost:8000/api/v1/dashboard/overview?status=completed

# Get 50 repositories
curl http://localhost:8000/api/v1/dashboard/overview?limit=50
```

```python
import requests

# Get all completed repositories
response = requests.get(
    "http://localhost:8000/api/v1/dashboard/overview",
    params={"status": "completed", "limit": 50}
)
repositories = response.json()

for repo in repositories:
    print(f"{repo['name']}: {repo['statistics']['resources']} resources")
```

---

## Error Responses

### 404 Not Found

```json
{
  "detail": "Repository 999 not found"
}
```

### 500 Internal Server Error

```json
{
  "detail": "Failed to get repository dashboard: Database connection error"
}
```

---

## Use Cases

### 1. Dashboard Overview Page

Display key metrics for all repositories:

```python
import requests

# Get all repositories
repos = requests.get(
    "http://localhost:8000/api/v1/dashboard/overview",
    params={"limit": 100}
).json()

# Calculate totals
total_resources = sum(r['statistics']['resources'] for r in repos)
total_modules = sum(r['statistics']['modules'] for r in repos)

print(f"Total Repositories: {len(repos)}")
print(f"Total Resources: {total_resources}")
print(f"Total Modules: {total_modules}")
```

### 2. Repository Detail Page

Show complete information for a single repository:

```python
import requests

repo_id = 1

# Get dashboard data
dashboard = requests.get(
    f"http://localhost:8000/api/v1/dashboard/repo/{repo_id}"
).json()

# Get summary
summary = requests.get(
    f"http://localhost:8000/api/v1/dashboard/summary/{repo_id}"
).json()

# Display
print(f"Repository: {dashboard['name']}")
print(f"Status: {dashboard['status']}")
print(f"Resources: {dashboard['statistics']['resources']}")
print(f"\nSummary:")
print(summary['architecture_description'])
```

### 3. Graph Visualization

Fetch graph data for visualization:

```python
import requests

repo_id = 1

# Get graph data
graph = requests.get(
    f"http://localhost:8000/api/v1/dashboard/graph/{repo_id}"
).json()

# Process for visualization library
nodes = graph['nodes']
edges = graph['edges']

print(f"Nodes: {len(nodes)}")
print(f"Edges: {len(edges)}")
print(f"Complexity: {graph['statistics']['complexity_metrics']}")
```

### 4. Statistics Comparison

Compare multiple repositories:

```python
import requests

repo_ids = [1, 2, 3]
comparisons = []

for repo_id in repo_ids:
    dashboard = requests.get(
        f"http://localhost:8000/api/v1/dashboard/repo/{repo_id}"
    ).json()
    
    comparisons.append({
        'name': dashboard['name'],
        'resources': dashboard['statistics']['resources'],
        'complexity': dashboard['graph_statistics']['total_edges']
    })

# Sort by complexity
comparisons.sort(key=lambda x: x['complexity'], reverse=True)

for comp in comparisons:
    print(f"{comp['name']}: {comp['resources']} resources, {comp['complexity']} dependencies")
```

---

## Integration with Frontend

### React Example

```typescript
import { useEffect, useState } from 'react';

interface DashboardData {
  id: number;
  name: string;
  statistics: {
    resources: number;
    modules: number;
    dependencies: number;
  };
}

function RepositoryDashboard({ repoId }: { repoId: number }) {
  const [dashboard, setDashboard] = useState<DashboardData | null>(null);
  
  useEffect(() => {
    fetch(`http://localhost:8000/api/v1/dashboard/repo/${repoId}`)
      .then(res => res.json())
      .then(data => setDashboard(data));
  }, [repoId]);
  
  if (!dashboard) return <div>Loading...</div>;
  
  return (
    <div>
      <h1>{dashboard.name}</h1>
      <div>
        <p>Resources: {dashboard.statistics.resources}</p>
        <p>Modules: {dashboard.statistics.modules}</p>
        <p>Dependencies: {dashboard.statistics.dependencies}</p>
      </div>
    </div>
  );
}
```

---

## Performance Considerations

### Response Times

- **Dashboard endpoint**: ~50-200ms
- **Summary endpoint**: ~20-50ms
- **Graph endpoint**: ~100-500ms (depends on graph size)
- **Overview endpoint**: ~50-200ms (depends on limit)

### Optimization Tips

1. **Use pagination** for overview endpoint
2. **Cache dashboard data** on frontend
3. **Fetch graph data** only when needed
4. **Filter by status** to reduce data transfer

---

## Related Documentation

- [Analysis Workflow](ANALYSIS_WORKFLOW.md)
- [API Documentation](API.md)
- [Quick Start Guide](QUICKSTART_ANALYSIS.md)