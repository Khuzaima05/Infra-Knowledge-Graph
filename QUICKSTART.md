# Quick Start Guide

## 5-Minute Setup

### Prerequisites
- Docker & Docker Compose
- Git

### Steps

1. **Clone and navigate to the project**
   ```bash
   cd Infra-Knowledge-Graph
   ```

2. **Run the setup script**
   ```bash
   chmod +x setup.sh
   ./setup.sh
   ```

3. **Open your browser**
   - Frontend: http://localhost:3000
   - API Docs: http://localhost:8000/docs

## First Analysis

### Using the Sample Terraform Config

1. Go to http://localhost:3000/dashboard
2. In the "Analyze Repository" form, you have two options:

   **Option A: Use the sample included in the project**
   - This requires pushing the sample-terraform folder to a GitHub repository first
   - Then use that repository URL

   **Option B: Use an existing Terraform repository**
   - Enter any public Terraform repository URL
   - Example: `https://github.com/terraform-aws-modules/terraform-aws-vpc`

3. Click "Analyze" and wait for completion

4. Once completed, click "View Graph" to explore the dependency graph

## Exploring the Graph

Once an analysis is complete, you can:

- **View the dependency graph** - See how resources connect
- **Click nodes** - View details about specific resources
- **Zoom and pan** - Navigate the graph using your mouse
- **View architecture summary** - Get AI-generated insights
- **See statistics** - Resource counts, module counts, etc.

## Key Features Explained

### Dependency Graph
Shows how Terraform resources, variables, modules, and providers relate to each other.
- Blue nodes = Resources
- Green nodes = Variables
- Purple nodes = Modules
- Orange nodes = Providers
- Cyan nodes = Outputs

### Architecture Summary
An automatically generated summary describing:
- What providers are used
- What modules are included
- Total resource count
- Deployment strategy

### Repository Dashboard
Shows all analyzed repositories with:
- Total resources
- Total modules
- Total variables
- Provider count
- Analysis status

## Stopping the Services

```bash
# Stop all containers
docker-compose down

# Clean up volumes too
docker-compose down -v
```

## Troubleshooting

### Services won't start

```bash
# Check Docker is running
docker --version

# View detailed logs
docker-compose logs backend
docker-compose logs frontend
```

### Database connection error

```bash
# Restart database
docker-compose restart postgres

# Wait and try again
sleep 5
docker-compose logs postgres
```

### Port already in use

If port 3000 or 8000 is already in use, edit `.env`:
```env
FRONTEND_PORT=3001  # Changed from 3000
BACKEND_PORT=8001   # Changed from 8000
```

Then restart:
```bash
docker-compose down
docker-compose up -d
```

## Next Steps

- Read the [full README](README.md)
- Check the [API Documentation](API.md)
- Review [Development Guide](DEVELOPMENT.md)
- Customize the deployment

## Support

For issues or questions:
1. Check the logs: `docker-compose logs -f`
2. Review the README.md
3. Check the API documentation
4. Look at the code comments

Enjoy analyzing your infrastructure! 🎉
