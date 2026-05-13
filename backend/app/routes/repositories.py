from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.database import get_db
from models.models import Repository, Module, Resource, Variable, Output, Provider
from services.analysis_service import RepositoryService
from typing import List

router = APIRouter()


@router.get("")
def list_repositories(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """List all analyzed repositories"""
    service = RepositoryService(db)
    repos = service.list_repositories(skip, limit)
    
    return [
        {
            "id": repo.id,
            "name": repo.name,
            "url": repo.url,
            "status": repo.status,
            "total_resources": repo.total_resources,
            "total_modules": repo.total_modules,
            "total_variables": repo.total_variables,
            "providers_count": repo.providers_count,
            "analyzed_at": repo.analyzed_at
        }
        for repo in repos
    ]


@router.get("/{repo_id}")
def get_repository(repo_id: int, db: Session = Depends(get_db)):
    """Get detailed repository information"""
    service = RepositoryService(db)
    repo = service.get_repository(repo_id)
    
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    return {
        "id": repo.id,
        "name": repo.name,
        "url": repo.url,
        "branch": repo.branch,
        "status": repo.status,
        "statistics": {
            "total_resources": repo.total_resources,
            "total_modules": repo.total_modules,
            "total_variables": repo.total_variables,
            "total_outputs": repo.total_outputs,
            "providers_count": repo.providers_count
        },
        "analyzed_at": repo.analyzed_at,
        "created_at": repo.created_at
    }


@router.get("/{repo_id}/modules")
def get_repository_modules(repo_id: int, db: Session = Depends(get_db)):
    """Get all modules in a repository"""
    repo = db.query(Repository).filter_by(id=repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    modules = db.query(Module).filter_by(repository_id=repo_id).all()
    
    return [
        {
            "id": module.id,
            "name": module.name,
            "source": module.source,
            "version": module.version,
            "metadata": module.metadata
        }
        for module in modules
    ]


@router.get("/{repo_id}/resources")
def get_repository_resources(repo_id: int, db: Session = Depends(get_db)):
    """Get all resources in a repository"""
    repo = db.query(Repository).filter_by(id=repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    resources = db.query(Resource).filter_by(repository_id=repo_id).all()
    
    return [
        {
            "id": resource.id,
            "type": resource.type,
            "name": resource.name,
            "full_name": resource.full_name,
            "provider": resource.provider,
            "metadata": resource.metadata
        }
        for resource in resources
    ]


@router.get("/{repo_id}/variables")
def get_repository_variables(repo_id: int, db: Session = Depends(get_db)):
    """Get all variables in a repository"""
    repo = db.query(Repository).filter_by(id=repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    variables = db.query(Variable).filter_by(repository_id=repo_id).all()
    
    return [
        {
            "id": var.id,
            "name": var.name,
            "type": var.type,
            "default_value": var.default_value,
            "description": var.description
        }
        for var in variables
    ]


@router.get("/{repo_id}/providers")
def get_repository_providers(repo_id: int, db: Session = Depends(get_db)):
    """Get all providers in a repository"""
    repo = db.query(Repository).filter_by(id=repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail="Repository not found")
    
    providers = db.query(Provider).filter_by(repository_id=repo_id).all()
    
    return [
        {
            "id": provider.id,
            "name": provider.name,
            "version": provider.version,
            "alias": provider.alias
        }
        for provider in providers
    ]
