# Development Guide

## Local Development Setup

### Prerequisites
- Python 3.11+
- Node.js 20+
- PostgreSQL 16+
- Git

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp ../.env.example .env

# Initialize database
python scripts/init_db.py

# Run development server
uvicorn app.main:app --reload
```

The backend will be available at `http://localhost:8000`.

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local file
echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local

# Run development server
npm run dev
```

The frontend will be available at `http://localhost:3000`.

## Project Architecture

### Backend Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI application setup
│   ├── routes/              # API endpoints
│   │   ├── analysis.py      # /api/analysis endpoints
│   │   ├── repositories.py  # /api/repositories endpoints
│   │   └── graphs.py        # /api/graphs endpoints
│   ├── schemas.py           # Pydantic models
│   ├── middleware.py        # Middleware
│   ├── utils.py             # Utility functions
│   └── exceptions.py        # Custom exceptions
├── parser/
│   ├── terraform_parser.py  # HCL2 parsing logic
│   └── repository_manager.py # Git repository management
├── graph/
│   └── graph_builder.py     # Graph generation and analysis
├── models/
│   ├── database.py          # Database setup
│   └── models.py            # SQLAlchemy ORM models
├── services/
│   └── analysis_service.py  # Business logic
├── config/
│   ├── settings.py          # Configuration
│   └── logger.py            # Logging setup
└── scripts/
    ├── init_db.py           # Database initialization
    └── test_parser.py       # Parser testing
```

### Frontend Structure

```
frontend/
├── app/
│   ├── page.tsx             # Home page
│   ├── layout.tsx           # Root layout
│   ├── globals.css          # Global styles
│   ├── dashboard/
│   │   ├── page.tsx         # Dashboard
│   │   └── layout.tsx       # Dashboard layout
│   ├── repositories/
│   │   └── page.tsx         # Repositories list
│   └── graph/
│       └── [id]/
│           └── page.tsx     # Graph visualization
├── components/
│   ├── RepositoryForm.tsx   # Repository submission form
│   ├── RepositoryList.tsx   # Repository listing
│   ├── GraphViewer.tsx      # Graph visualization
│   └── graph/
│       ├── ResourceNode.tsx
│       ├── VariableNode.tsx
│       ├── ModuleNode.tsx
│       ├── ProviderNode.tsx
│       └── OutputNode.tsx
├── lib/
│   ├── api.ts               # API client
│   ├── store.ts             # Zustand stores
│   ├── graph-store.ts       # Graph state management
│   └── utils.ts             # Utility functions
└── public/                  # Static assets
```

## Development Workflow

### Adding a New Endpoint

1. **Create the route handler** in `backend/app/routes/`:

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from models.database import get_db

router = APIRouter()

@router.get("/example")
def get_example(db: Session = Depends(get_db)):
    """Description of the endpoint"""
    return {"message": "Hello"}
```

2. **Register the router** in `backend/app/main.py`:

```python
from app.routes import example
app.include_router(example.router, prefix="/api/example", tags=["example"])
```

3. **Create Pydantic schema** in `backend/app/schemas.py`:

```python
class ExampleRequest(BaseModel):
    name: str

class ExampleResponse(BaseModel):
    id: int
    name: str
```

### Adding a New Frontend Component

1. **Create the component** in `frontend/components/`:

```typescript
// components/MyComponent.tsx
export default function MyComponent({ prop }: { prop: string }) {
  return <div>{prop}</div>
}
```

2. **Use it in a page**:

```typescript
// app/page.tsx
import MyComponent from '@/components/MyComponent'

export default function Page() {
  return <MyComponent prop="value" />
}
```

## Database Migrations

Currently using SQLAlchemy direct model management. To add a new model:

1. **Define the model** in `backend/models/models.py`:

```python
class NewModel(Base):
    __tablename__ = "new_models"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
```

2. **Run database initialization**:

```bash
python backend/scripts/init_db.py
```

## Testing

### Backend Tests

```bash
cd backend
pytest
```

### Frontend Tests

```bash
cd frontend
npm test
```

## Common Tasks

### Restart Services

```bash
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart backend
docker-compose restart frontend
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Database Debugging

```bash
# Connect to database
docker-compose exec postgres psql -U ikg_user -d ikg_db

# Common queries
SELECT * FROM repositories;
SELECT * FROM resources LIMIT 10;
SELECT * FROM graphs;
```

### Clean Rebuild

```bash
./cleanup.sh
./setup.sh
```

## Debugging

### Backend Debugging

Use FastAPI's built-in debugging:
```python
from config.logger import logger

logger.info("Information message")
logger.error("Error message", exc_info=True)
```

Access API docs at `http://localhost:8000/docs` for interactive testing.

### Frontend Debugging

Use browser DevTools:
1. Open Chrome/Firefox DevTools (F12)
2. Check Console for errors
3. Use React DevTools extension
4. Check Network tab for API calls

## Performance Tips

### Backend
- Use database indexes for frequently queried fields
- Implement pagination for large result sets
- Use connection pooling

### Frontend
- Use React.memo for expensive components
- Implement code splitting with next/dynamic
- Optimize images using next/image

## Environment Variables

Create `.env.local` files for local development:

**Backend (.env)**
```env
DATABASE_URL=postgresql://ikg_user:ikg_password@localhost:5432/ikg_db
ENVIRONMENT=development
LOG_LEVEL=DEBUG
```

**Frontend (.env.local)**
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Troubleshooting

### Port Already in Use

```bash
# Find process on port 3000
lsof -i :3000
# Kill process
kill -9 <PID>
```

### Database Connection Issues

```bash
# Restart database
docker-compose restart postgres

# Check connectivity
docker-compose exec backend python -c "from models.database import engine; print(engine.connect())"
```

### Module Import Errors

```bash
# Ensure venv is activated
source backend/venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

## Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com)
- [Next.js Documentation](https://nextjs.org/docs)
- [React Flow Documentation](https://reactflow.dev)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org)
- [Terraform Documentation](https://www.terraform.io/docs)
