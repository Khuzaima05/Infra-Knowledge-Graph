from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exception_handlers import HTTPException
from config.settings import settings
from config.logger import logger
from models.database import init_db
from app.exceptions import AnalysisException
from app.middleware import exception_handler

# Initialize database
try:
    init_db()
    logger.info("Database initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize database: {str(e)}")
    raise

app = FastAPI(
    title=settings.app_name,
    description="Infrastructure dependency graph analysis tool for Terraform",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add exception handlers
app.add_exception_handler(AnalysisException, exception_handler)
app.add_exception_handler(Exception, exception_handler)

# Import and include routers
from app.routes import analysis, repositories, graphs, ingestion, dashboard

app.include_router(analysis.router, prefix=f"{settings.api_prefix}/analysis", tags=["analysis"])
app.include_router(repositories.router, prefix=f"{settings.api_prefix}/repositories", tags=["repositories"])
app.include_router(graphs.router, prefix=f"{settings.api_prefix}/graphs", tags=["graphs"])
app.include_router(ingestion.router, prefix=f"{settings.api_prefix}/ingestion", tags=["ingestion"])
app.include_router(dashboard.router, prefix=f"{settings.api_prefix}/dashboard", tags=["dashboard"])


@app.get("/")
def read_root():
    """Root endpoint"""
    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy"
    }
