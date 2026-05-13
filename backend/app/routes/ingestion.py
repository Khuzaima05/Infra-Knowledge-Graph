"""Repository Ingestion API Routes

Endpoints for GitHub repository ingestion, validation, and management.
"""

from fastapi import APIRouter, HTTPException, status
from typing import Dict, Any
from config.logger import logger
from config.settings import settings
from app.schemas import (
    RepoIngestionRequest,
    RepoMetadataResponse,
    TerraformFilesResponse,
    StorageUsageResponse,
    CleanupStatsResponse
)
from services.repo_ingestion_service import (
    RepoIngestionService,
    RepositoryValidationError,
    RepositoryIngestionError
)

router = APIRouter()

# Initialize ingestion service
ingestion_service = RepoIngestionService(workspace_dir=settings.tf_workspace_dir)


@router.post("/ingest", response_model=RepoMetadataResponse, status_code=status.HTTP_201_CREATED)
async def ingest_repository(request: RepoIngestionRequest) -> Dict[str, Any]:
    """
    Ingest a GitHub repository by cloning it locally.
    
    - **url**: GitHub repository URL (HTTPS or SSH format)
    - **branch**: Git branch to clone (default: main)
    - **force_refresh**: Force re-clone if repository already exists
    
    Returns repository metadata including commit information.
    """
    try:
        logger.info(f"Ingesting repository: {request.url}")
        
        # Clone repository and get metadata
        metadata = ingestion_service.clone_repository(
            url=request.url,
            branch=request.branch or "main",
            force_refresh=request.force_refresh or False
        )
        
        logger.info(f"Successfully ingested: {metadata['owner']}/{metadata['name']}")
        return metadata
    
    except RepositoryValidationError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except RepositoryIngestionError as e:
        logger.error(f"Ingestion error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to ingest repository: {str(e)}"
        )
    
    except Exception as e:
        logger.error(f"Unexpected error during ingestion: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during repository ingestion"
        )


@router.post("/validate")
async def validate_repository_url(url: str) -> Dict[str, Any]:
    """
    Validate a GitHub repository URL without cloning.
    
    - **url**: GitHub repository URL to validate
    
    Returns parsed repository information if valid.
    """
    try:
        logger.info(f"Validating URL: {url}")
        
        # Parse and validate URL
        repo_info = ingestion_service.parse_github_url(url)
        
        return {
            "valid": True,
            "owner": repo_info['owner'],
            "name": repo_info['name'],
            "url": repo_info['url']
        }
    
    except RepositoryValidationError as e:
        logger.warning(f"Invalid URL: {url} - {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/terraform-files/{owner}/{repo}", response_model=TerraformFilesResponse)
async def get_terraform_files(owner: str, repo: str) -> Dict[str, Any]:
    """
    Get list of all Terraform files in a cloned repository.
    
    - **owner**: Repository owner
    - **repo**: Repository name
    
    Returns list of Terraform file paths relative to repository root.
    """
    try:
        logger.info(f"Scanning Terraform files in {owner}/{repo}")
        
        # Check if repository exists
        if not ingestion_service.repository_exists(owner, repo):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Repository {owner}/{repo} not found. Please ingest it first."
            )
        
        # Find all Terraform files
        terraform_files = ingestion_service.find_terraform_files(owner, repo)
        
        return {
            "owner": owner,
            "name": repo,
            "terraform_files": terraform_files,
            "total_files": len(terraform_files)
        }
    
    except RepositoryIngestionError as e:
        logger.error(f"Error scanning files: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.get("/terraform-files/{owner}/{repo}/{file_path:path}")
async def get_terraform_file_content(owner: str, repo: str, file_path: str) -> Dict[str, str]:
    """
    Get content of a specific Terraform file.
    
    - **owner**: Repository owner
    - **repo**: Repository name
    - **file_path**: Relative path to the Terraform file
    
    Returns file path and content.
    """
    try:
        logger.info(f"Reading file: {owner}/{repo}/{file_path}")
        
        # Check if repository exists
        if not ingestion_service.repository_exists(owner, repo):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Repository {owner}/{repo} not found"
            )
        
        # Read file content
        path, content = ingestion_service.get_terraform_file_content(owner, repo, file_path)
        
        return {
            "file_path": path,
            "content": content
        }
    
    except RepositoryIngestionError as e:
        logger.error(f"Error reading file: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@router.delete("/{owner}/{repo}")
async def delete_repository(owner: str, repo: str) -> Dict[str, Any]:
    """
    Delete a cloned repository from local storage.
    
    - **owner**: Repository owner
    - **repo**: Repository name
    
    Returns deletion status.
    """
    try:
        logger.info(f"Deleting repository: {owner}/{repo}")
        
        deleted = ingestion_service.delete_repository(owner, repo)
        
        if not deleted:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Repository {owner}/{repo} not found"
            )
        
        return {
            "success": True,
            "message": f"Repository {owner}/{repo} deleted successfully"
        }
    
    except RepositoryIngestionError as e:
        logger.error(f"Error deleting repository: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


@router.post("/cleanup", response_model=CleanupStatsResponse)
async def cleanup_old_repositories(max_age_days: int = 30) -> Dict[str, int]:
    """
    Clean up repositories older than specified age.
    
    - **max_age_days**: Maximum age in days (default: 30)
    
    Returns cleanup statistics.
    """
    try:
        logger.info(f"Starting cleanup for repositories older than {max_age_days} days")
        
        stats = ingestion_service.cleanup_old_repositories(max_age_days)
        
        logger.info(f"Cleanup completed: {stats}")
        return stats
    
    except Exception as e:
        logger.error(f"Error during cleanup: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Cleanup failed: {str(e)}"
        )


@router.get("/storage", response_model=StorageUsageResponse)
async def get_storage_usage() -> Dict[str, Any]:
    """
    Get storage usage statistics for all cloned repositories.
    
    Returns total storage used and repository count.
    """
    try:
        logger.info("Calculating storage usage")
        
        usage = ingestion_service.get_storage_usage()
        
        return usage
    
    except Exception as e:
        logger.error(f"Error calculating storage: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to calculate storage usage: {str(e)}"
        )


@router.get("/{owner}/{repo}/exists")
async def check_repository_exists(owner: str, repo: str) -> Dict[str, Any]:
    """
    Check if a repository is already cloned locally.
    
    - **owner**: Repository owner
    - **repo**: Repository name
    
    Returns existence status.
    """
    exists = ingestion_service.repository_exists(owner, repo)
    
    return {
        "exists": exists,
        "owner": owner,
        "name": repo
    }

# Made with Bob
