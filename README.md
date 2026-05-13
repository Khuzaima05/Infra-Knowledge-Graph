# Infrastructure Knowledge Graph

> Visualize and analyze Terraform infrastructure dependencies with an interactive knowledge graph

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Next.js 15](https://img.shields.io/badge/Next.js-15-black)](https://nextjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![IBM Cloud](https://img.shields.io/badge/IBM%20Cloud-Ready-blue)](https://cloud.ibm.com/)

## 🚀 Features

### Core Capabilities
- **🔍 Repository Analysis**: Clone and parse any public Terraform repository
- **📊 Dependency Graphs**: Interactive visualization of infrastructure dependencies
- **🔎 Smart Search**: Command palette (Cmd/Ctrl+K) for instant node navigation
- **📝 Architecture Summaries**: Auto-generated infrastructure insights
- **🎯 Real-time Analysis**: Background processing with progress tracking
- **🌐 Multi-Cloud Support**: IBM Cloud, AWS, GCP, Azure, Kubernetes, and more
- **🏢 IBM Cloud Optimized**: Special support for terraform-ibm-modules

### Technical Features
- **Graph Visualization**: React Flow-based interactive dependency graphs
- **Metadata-Based Analysis**: No external AI APIs required
- **RESTful API**: Complete FastAPI backend with OpenAPI docs
- **Type-Safe**: Full TypeScript frontend with Pydantic backend
- **Dark Theme**: Modern developer-focused UI
- **Responsive Design**: Works on desktop and tablet

## 📸 Screenshots

### Dashboard
![Dashboard](docs/images/dashboard.png)

### Dependency Graph
![Graph Visualization](docs/images/graph.png)

### Architecture Summary
![Summary](docs/images/summary.png)

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Next.js 15)                    │
│  • React 19 with TypeScript                                  │
│  • Tailwind CSS for styling                                  │
│  • React Flow for graph visualization                        │
│  • Command palette for search                                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼ REST API
┌─────────────────────────────────────────────────────────────┐
│                    Backend (FastAPI)                         │
│  • Repository ingestion service                              │
│  • Terraform parser (python-hcl2)                            │
│  • Graph builder (NetworkX)                                  │
│  • Summary generator                                         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                  Database (PostgreSQL/SQLite)                │
│  • Repositories, Resources, Modules                          │
│  • Variables, Outputs, Providers                             │
│  • Graphs, Summaries, Relationships                          │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Node.js 18+
- Git

### 1. Clone Repository
```bash
git clone https://github.com/Khuzaima05/Infra-Knowledge-Graph.git
cd Infra-Knowledge-Graph
```

### 2. Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python scripts/init_db.py

# Start server
uvicorn app.main:app --reload
```

Backend will be available at http://localhost:8000

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend will be available at http://localhost:3000

### 4. Try It Out

1. Open http://localhost:3000
2. Click "Add Repository"
3. Enter a Terraform repository URL (e.g., `https://github.com/terraform-aws-modules/terraform-aws-vpc`)
4. Click "Analyze Repository"
5. View the dependency graph and architecture summary

## 📚 Documentation

### User Guides
- [Quick Start Guide](QUICKSTART.md) - Get started in 5 minutes
- [User Guide](docs/USER_GUIDE.md) - Complete feature walkthrough
- [API Documentation](API.md) - REST API reference

### Developer Guides
- [Architecture Guide](ARCHITECTURE.md) - System design and components
- [Development Guide](DEVELOPMENT.md) - Setup and contribution guide
- [Deployment Guide](DEPLOYMENT.md) - Production deployment instructions

### Feature Documentation
- [Analysis Workflow](ANALYSIS_WORKFLOW.md) - Repository analysis process
- [Terraform Parser](TERRAFORM_PARSER.md) - HCL parsing implementation
- [Graph Builder](docs/GRAPH_BUILDER.md) - Dependency graph construction
- [Summary Generator](ARCHITECTURE_SUMMARY.md) - Architecture summary generation
- [Dashboard API](DASHBOARD_API.md) - Statistics and metrics endpoints

## 🎯 Use Cases

### Infrastructure Auditing
- Visualize resource dependencies
- Identify circular dependencies
- Find unused resources
- Analyze module relationships

### Documentation
- Auto-generate architecture diagrams
- Create infrastructure summaries
- Document provider usage
- Track configuration complexity

### Code Review
- Understand infrastructure changes
- Review dependency impacts
- Validate module usage
- Check best practices

### Learning
- Explore Terraform repositories
- Understand infrastructure patterns
- Learn from real-world examples
- Study multi-cloud architectures

## 🛠️ Technology Stack

### Backend
- **Framework**: FastAPI 0.104+
- **Parser**: python-hcl2 4.3+
- **Graph**: NetworkX 3.2+
- **Database**: SQLAlchemy 2.0+ (PostgreSQL/SQLite)
- **Git**: GitPython 3.1+
- **Testing**: pytest 7.4+

### Frontend
- **Framework**: Next.js 15
- **UI Library**: React 19
- **Styling**: Tailwind CSS 3.4
- **Graph**: React Flow 11.10
- **Icons**: Lucide React
- **HTTP**: Axios
- **State**: React Hooks

## 📊 API Endpoints

### Analysis
- `POST /api/analysis/analyze` - Analyze repository
- `GET /api/analysis/repositories/{id}/status` - Get analysis status
- `GET /api/analysis/repositories/{id}/summary` - Get architecture summary

### Graphs
- `GET /api/graphs/{id}/dependency-graph` - Get dependency graph
- `GET /api/graphs/{id}/search` - Search graph nodes
- `GET /api/graphs/{id}/nodes/{node_id}` - Get node details

### Dashboard
- `GET /api/dashboard` - Get overview statistics
- `GET /api/dashboard/repo/{id}` - Get repository dashboard

### Repositories
- `GET /api/repositories` - List repositories
- `GET /api/repositories/{id}` - Get repository details
- `DELETE /api/repositories/{id}` - Delete repository

Full API documentation: http://localhost:8000/docs

## 🔍 Search & Navigation

### Command Palette
Press **Cmd/Ctrl + K** to open the command palette:
- Search nodes by name, type, or ID
- Navigate instantly to any node
- Filter by node type
- Keyboard-driven interface

### Graph Controls
- **Pan**: Click and drag
- **Zoom**: Mouse wheel or pinch
- **Select**: Click on node
- **Search**: Use search bar or command palette
- **Filter**: Filter by node type
- **Fullscreen**: Toggle fullscreen mode

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/ -v
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Integration Tests
```bash
# Start backend
cd backend && uvicorn app.main:app &

# Run integration tests
cd frontend && npm run test:e2e
```

## 🚀 Deployment

### Quick Deploy

**Frontend (Vercel):**
```bash
cd frontend
vercel --prod
```

**Backend (Railway):**
```bash
cd backend
railway up
```

See [DEPLOYMENT.md](DEPLOYMENT.md) for detailed instructions.

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Development Setup
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

### Code Style
- **Backend**: Black, isort, flake8
- **Frontend**: ESLint, Prettier
- **Commits**: Conventional Commits

## 📝 License

This project is licensed under the MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Terraform](https://www.terraform.io/) - Infrastructure as Code
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [Next.js](https://nextjs.org/) - React framework
- [React Flow](https://reactflow.dev/) - Graph visualization
- [python-hcl2](https://github.com/amplify-education/python-hcl2) - HCL parser

## 📧 Contact

- **GitHub**: [@Khuzaima05](https://github.com/Khuzaima05)
- **Issues**: [GitHub Issues](https://github.com/Khuzaima05/Infra-Knowledge-Graph/issues)

## 🗺️ Roadmap

### v1.1 (Q2 2024)
- [ ] Private repository support
- [ ] Multi-branch analysis
- [ ] Export to PNG/SVG
- [ ] Custom graph layouts

### v1.2 (Q3 2024)
- [ ] Terraform state file analysis
- [ ] Cost estimation integration
- [ ] Security scanning
- [ ] Compliance checking

### v2.0 (Q4 2024)
- [ ] Real-time collaboration
- [ ] Version comparison
- [ ] AI-powered insights (optional)
- [ ] Custom plugins

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=Khuzaima05/Infra-Knowledge-Graph&type=Date)](https://star-history.com/#Khuzaima05/Infra-Knowledge-Graph&Date)

---

**Made with ❤️ by Bob** - Infrastructure Knowledge Graph
