# Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    INFRA KNOWLEDGE GRAPH                    │
└─────────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────────┐
│                    FRONTEND LAYER (Next.js)                  │
├──────────────────────────────────────────────────────────────┤
│ • Landing Page          • Dashboard                          │
│ • Repository Form       • Graph Viewer                       │
│ • Repository List       • Architecture Summary               │
│ • Node Details Panel    • Statistics                         │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    HTTP/REST API (FastAPI)
                              │
┌──────────────────────────────────────────────────────────────┐
│                    BACKEND LAYER (FastAPI)                   │
├──────────────────────────────────────────────────────────────┤
│                         Routes Layer                          │
│ /api/analysis    /api/repositories    /api/graphs            │
│                                                              │
│                      Services Layer                          │
│ AnalysisService       RepositoryService                      │
│                                                              │
│                    Parsing & Analysis Layer                  │
│ TerraformParser    RepositoryManager    GraphBuilder         │
│                                                              │
│                     Database Access Layer                    │
│ SQLAlchemy ORM    Database Models      Database Session      │
└──────────────────────────────────────────────────────────────┘
                              │
                              ▼
             ┌─────────────────────────────────┐
             │   PostgreSQL Database           │
             ├─────────────────────────────────┤
             │ repositories     terraform_files │
             │ modules          resources       │
             │ variables        outputs         │
             │ providers        relationships   │
             │ graphs           summaries       │
             └─────────────────────────────────┘
```

## Data Flow

### 1. Repository Analysis Flow

```
User submits URL
    ↓
[RepositoryManager] Clone from GitHub
    ↓
[TerraformParser] Find .tf files
    ↓
[HCL2 Parser] Parse each file
    ↓
[Parser] Extract:
  • Modules
  • Resources
  • Variables
  • Outputs
  • Providers
  • References
    ↓
[Database] Save all components
    ↓
[GraphBuilder] Create dependency graph
    ↓
[Database] Save graph nodes & edges
    ↓
[SummaryGenerator] Create architecture summary
    ↓
[Database] Save summary
    ↓
Return to user
```

### 2. Graph Request Flow

```
Frontend requests /api/graphs/{repo_id}/dependency-graph
    ↓
Backend retrieves saved graph from database
    ↓
Convert to React Flow format
    ↓
Return JSON with nodes and edges
    ↓
Frontend renders with React Flow
    ↓
User can interact with graph
```

## Component Responsibilities

### Parser Module (`backend/parser/`)

**TerraformParser**
- Finds Terraform files (.tf)
- Parses HCL2 syntax
- Extracts infrastructure components
- Detects references between components
- Handles parsing errors gracefully

**RepositoryManager**
- Clones repositories from GitHub
- Manages local repository cache
- Validates repository URLs
- Handles git operations
- Manages repository lifecycle

### Graph Module (`backend/graph/`)

**GraphBuilder**
- Creates NetworkX directed graph
- Adds nodes for each infrastructure component
- Builds edges based on references
- Generates visualization JSON
- Calculates graph statistics

**DependencyAnalyzer**
- Analyzes dependency chains
- Finds circular dependencies
- Calculates critical paths
- Identifies isolated components

### Services Module (`backend/services/`)

**AnalysisService**
- Orchestrates complete analysis
- Coordinates parser, graph builder, and database
- Handles error recovery
- Manages transaction lifecycle

**RepositoryService**
- CRUD operations for repositories
- Graph retrieval
- Summary retrieval
- Repository statistics

### API Routes (`backend/app/routes/`)

**analysis.py**
- POST /api/analysis - Trigger analysis
- GET /api/analysis/{repo_id}/status - Check status

**repositories.py**
- GET /api/repositories - List all
- GET /api/repositories/{repo_id} - Get details
- GET /api/repositories/{repo_id}/modules - Get modules
- GET /api/repositories/{repo_id}/resources - Get resources
- GET /api/repositories/{repo_id}/variables - Get variables
- GET /api/repositories/{repo_id}/providers - Get providers

**graphs.py**
- GET /api/graphs/{repo_id}/dependency-graph - Get graph
- GET /api/graphs/{repo_id}/summary - Get summary

## Database Schema

```
repositories
├── id (PK)
├── name
├── url (UNIQUE)
├── branch
├── status
├── statistics
├── timestamps
└── relationships
    ├── terraform_files (1:N)
    ├── graph (1:1)
    └── summary (1:1)

terraform_files
├── id (PK)
├── repository_id (FK)
├── file_path
├── content
└── relationships
    ├── modules (1:N)
    ├── resources (1:N)
    └── variables (1:N)

modules
├── id (PK)
├── repository_id (FK)
├── name
├── source
├── version
└── metadata

resources
├── id (PK)
├── repository_id (FK)
├── type
├── name
├── provider
└── metadata

variables
├── id (PK)
├── repository_id (FK)
├── name
├── type
├── default_value
└── description

outputs
├── id (PK)
├── repository_id (FK)
├── name
├── value
└── description

providers
├── id (PK)
├── repository_id (FK)
├── name
├── version
└── alias

relationships
├── id (PK)
├── repository_id (FK)
├── source_type
├── source_id
├── target_type
├── target_id
└── relationship_type

graphs
├── id (PK)
├── repository_id (FK, UNIQUE)
├── nodes (JSON)
├── edges (JSON)
└── statistics

summaries
├── id (PK)
├── repository_id (FK, UNIQUE)
├── title
├── architecture_description
├── key_components
└── deployment_overview
```

## Frontend Components

### Pages
- `/` - Home page with feature overview
- `/dashboard` - Main dashboard with form and list
- `/repositories` - Repositories table view
- `/graph/[id]` - Graph visualization page

### Components
- `RepositoryForm` - Submit new repository for analysis
- `RepositoryList` - Display analyzed repositories
- `GraphViewer` - React Flow graph visualization
- Graph Nodes:
  - `ResourceNode` - Blue colored
  - `VariableNode` - Green colored
  - `ModuleNode` - Purple colored
  - `ProviderNode` - Orange colored
  - `OutputNode` - Cyan colored

### State Management
- Zustand stores for global state
- React hooks for component state
- React Flow built-in state management

## Deployment Architecture

### Docker Structure

```
docker-compose.yml
├── postgres:16-alpine
│   └── Volume: postgres_data
├── backend:latest
│   ├── Source: backend/Dockerfile
│   ├── Volume: app code
│   └── Depends on: postgres
├── frontend:latest
│   ├── Source: frontend/Dockerfile
│   ├── Volume: app code
│   └── Depends on: backend
└── Volumes
    ├── postgres_data
    └── repo_cache

Ports:
├── 5432 - PostgreSQL
├── 8000 - FastAPI Backend
└── 3000 - Next.js Frontend
```

## Performance Considerations

### Backend
- HCL2 parsing is CPU-bound
- Large repositories may take time
- Caching strategies for repeated analysis
- Database indexing on frequently queried fields

### Frontend
- React Flow handles large graphs efficiently
- Lazy loading for heavy computations
- Client-side graph filtering

### Database
- Connection pooling for multiple requests
- Indexed queries on repository and foreign keys
- JSON storage for flexible metadata

## Security Considerations

Current implementation (V1):
- No authentication (planned for V2)
- Public repository access only (GitHub public repos)
- Local repository caching
- No data encryption (use HTTPS in production)

Future considerations:
- User authentication
- Authorization levels
- Private repository support
- Audit logging
- Rate limiting
- API key authentication

## Scalability Path

Future improvements:
- Kubernetes deployment
- Distributed parsing (e.g., Celery)
- Redis caching layer
- Search indexing (Elasticsearch)
- Microservices architecture
- GraphQL API
- WebSocket support for real-time updates

---

For more details, see [DEVELOPMENT.md](DEVELOPMENT.md) and [API.md](API.md)
