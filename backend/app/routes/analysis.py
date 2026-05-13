"""Analysis API Routes

Endpoints for complete repository analysis workflow with async support.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Optional

from models.database import get_db
from models.models import Repository, Summary
from services.analysis_orchestrator import AnalysisOrchestrator, AnalysisError
from app.schemas import (
    CompleteAnalysisRequest,
    CompleteAnalysisResponse,
    AnalysisStatusResponse,
    RepositoryResponse,
    ArchitectureSummaryResponse,
    KeyComponent
)
from config.logger import logger

router = APIRouter()


def run_analysis_background(
    orchestrator: AnalysisOrchestrator,
    url: str,
    branch: str,
    force_refresh: bool
):
    """
    Background task for running analysis
    
    This runs in a separate thread and updates the database
    with progress and results.
    """
    try:
        logger.info(f"Background analysis started for {url}")
        orchestrator.analyze_repository(
            url=url,
            branch=branch,
            force_refresh=force_refresh
        )
        logger.info(f"Background analysis completed for {url}")
    except Exception as e:
        logger.exception(f"Background analysis failed for {url}: {str(e)}")


@router.post("/analyze", response_model=CompleteAnalysisResponse)
def analyze_repository(
    request: CompleteAnalysisRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """
    Analyze a Terraform repository with complete workflow
    
    **Workflow Steps:**
    1. Validate GitHub URL
    2. Clone repository locally
    3. Parse all Terraform files
    4. Resolve references and dependencies
    5. Build dependency graph
    6. Store metadata in database
    7. Generate architecture summary
    
    **Parameters:**
    - **url**: GitHub repository URL (https://github.com/owner/repo)
    - **branch**: Git branch to analyze (default: main)
    - **force_refresh**: Force re-clone if already exists (default: false)
    - **async_mode**: Run analysis in background (default: true)
    
    **Returns:**
    - Repository ID and status
    - If async_mode=true, analysis runs in background
    - If async_mode=false, waits for completion
    
    **Example:**
    ```json
    {
        "url": "https://github.com/terraform-aws-modules/terraform-aws-vpc",
        "branch": "main",
        "force_refresh": false,
        "async_mode": true
    }
    ```
    """
    try:
        orchestrator = AnalysisOrchestrator(db)
        
        # Validate URL first
        try:
            repo_info = orchestrator.ingestion_service.parse_github_url(request.url)
        except Exception as e:
            raise HTTPException(
                status_code=400,
                detail=f"Invalid GitHub URL: {str(e)}"
            )
        
        # Check if repository already exists
        from models.models import Repository
        existing_repo = db.query(Repository).filter_by(url=request.url).first()
        
        if request.async_mode:
            # Run in background
            if existing_repo:
                repo_id = existing_repo.id
                existing_repo.status = 'analyzing'
                db.commit()
            else:
                # Create placeholder record
                new_repo = Repository(
                    name=repo_info['name'],
                    url=request.url,
                    branch=request.branch,
                    status='analyzing'
                )
                db.add(new_repo)
                db.commit()
                repo_id = new_repo.id
            
            # Schedule background task
            background_tasks.add_task(
                run_analysis_background,
                orchestrator,
                request.url,
                request.branch,
                request.force_refresh
            )
            
            return CompleteAnalysisResponse(
                repository_id=repo_id,
                status='analyzing',
                message=f"Analysis started for {repo_info['name']}",
                analysis_started=True,
                estimated_time_seconds=60
            )
        
        else:
            # Run synchronously
            logger.info(f"Starting synchronous analysis for {request.url}")
            repo = orchestrator.analyze_repository(
                url=request.url,
                branch=request.branch or "main",
                force_refresh=request.force_refresh or False
            )
            
            return CompleteAnalysisResponse(
                repository_id=repo.id,
                status=repo.status,
                message=f"Analysis completed for {repo.name}",
                analysis_started=True,
                estimated_time_seconds=0
            )
    
    except AnalysisError as e:
        logger.error(f"Analysis error: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    
    except Exception as e:
        logger.exception(f"Unexpected error during analysis: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Analysis failed: {str(e)}"
        )


@router.get("/status/{repo_id}", response_model=AnalysisStatusResponse)
def get_analysis_status(repo_id: int, db: Session = Depends(get_db)):
    """
    Get current analysis status for a repository
    
    **Parameters:**
    - **repo_id**: Repository ID
    
    **Returns:**
    - Current status (pending, analyzing, completed, failed)
    - Statistics if completed
    - Error message if failed
    
    **Status Values:**
    - `pending`: Repository record created, analysis not started
    - `analyzing`: Analysis in progress
    - `completed`: Analysis finished successfully
    - `failed`: Analysis failed with error
    """
    orchestrator = AnalysisOrchestrator(db)
    status = orchestrator.get_analysis_status(repo_id)
    
    if not status:
        raise HTTPException(
            status_code=404,
            detail=f"Repository {repo_id} not found"
        )
    
    return AnalysisStatusResponse(**status)


@router.get("/repository/{repo_id}", response_model=RepositoryResponse)
def get_repository_details(repo_id: int, db: Session = Depends(get_db)):
    """
    Get complete repository details including analysis results
    
    **Parameters:**
    - **repo_id**: Repository ID
    
    **Returns:**
    - Repository metadata
    - Analysis statistics
    - Timestamps
    """
    from models.models import Repository
    
    repo = db.query(Repository).filter_by(id=repo_id).first()
    
    if not repo:
        raise HTTPException(
            status_code=404,
            detail=f"Repository {repo_id} not found"
        )
    
    return RepositoryResponse(
        id=repo.id,
        name=repo.name,
        url=repo.url,
        branch=repo.branch,
        status=repo.status,
        statistics={
            'total_resources': repo.total_resources,
            'total_modules': repo.total_modules,
            'total_variables': repo.total_variables,
            'total_outputs': repo.total_outputs,
            'providers_count': repo.providers_count
        },
        analyzed_at=repo.analyzed_at,
        created_at=repo.created_at
    )


@router.delete("/repository/{repo_id}")
def delete_repository_analysis(repo_id: int, db: Session = Depends(get_db)):
    """
    Delete repository analysis and all associated data
    
    **Parameters:**
    - **repo_id**: Repository ID
    
    **Returns:**
    - Success message
    
    **Note:** This also deletes the cloned repository from local storage
    """
    from models.models import Repository
    
    repo = db.query(Repository).filter_by(id=repo_id).first()
    
    if not repo:
        raise HTTPException(
            status_code=404,
            detail=f"Repository {repo_id} not found"
        )
    
    # Delete from local storage if exists
    if repo.cloned_path:
        try:
            orchestrator = AnalysisOrchestrator(db)
            repo_info = orchestrator.ingestion_service.parse_github_url(repo.url)
            orchestrator.ingestion_service.delete_repository(
                repo_info['owner'],
                repo_info['name']
            )
            logger.info(f"Deleted local repository: {repo.cloned_path}")
        except Exception as e:
            logger.warning(f"Failed to delete local repository: {str(e)}")
    
    # Delete from database (cascades to all related records)
    db.delete(repo)
    db.commit()
    
    return {
        "message": f"Repository {repo.name} deleted successfully",
        "repository_id": repo_id
    }

@router.get("/repositories/{repo_id}/summary", response_model=ArchitectureSummaryResponse)
async def get_architecture_summary(
    repo_id: int,
    db: Session = Depends(get_db)
):
    """
    Get architecture summary for a repository
    
    Returns comprehensive human-readable summary including:
    - Overview and title
    - Architecture description
    - Provider usage analysis
    - Module relationships
    - Networking overview
    - Infrastructure complexity insights
    - Key components
    - Deployment overview
    
    **Parameters:**
    - **repo_id**: Repository ID
    
    **Returns:**
    - ArchitectureSummaryResponse with complete summary
    
    **Raises:**
    - 404: Repository or summary not found
    """
    logger.info(f"Fetching architecture summary for repository {repo_id}")
    
    # Check repository exists
    repo = db.query(Repository).filter(Repository.id == repo_id).first()
    if not repo:
        raise HTTPException(status_code=404, detail=f"Repository {repo_id} not found")
    
    # Get summary
    summary = db.query(Summary).filter(Summary.repository_id == repo_id).first()
    if not summary:
        raise HTTPException(
            status_code=404,
            detail=f"Summary not found for repository {repo_id}. Run analysis first."
        )
    
    logger.info(f"Retrieved summary: {summary.title}")
    
    return ArchitectureSummaryResponse(
        repository_id=summary.repository_id,
        title=summary.title,
        architecture_description=summary.architecture_description,
        key_components=summary.key_components,
        deployment_overview=summary.deployment_overview,
        created_at=summary.created_at,
        updated_at=summary.updated_at
    )


@router.get("/repositories")
def list_repositories(
    skip: int = 0,
    limit: int = 10,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List all analyzed repositories with pagination
    
    **Parameters:**
    - **skip**: Number of records to skip (default: 0)
    - **limit**: Maximum number of records to return (default: 10)
    - **status**: Filter by status (pending, analyzing, completed, failed)
    
    **Returns:**
    - List of repositories with metadata
    - Total count
    """
    from models.models import Repository
    
    query = db.query(Repository)
    
    if status:
        query = query.filter_by(status=status)
    
    total = query.count()
    repositories = query.offset(skip).limit(limit).all()
    
    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "repositories": [
            {
                "id": repo.id,
                "name": repo.name,
                "url": repo.url,
                "status": repo.status,
                "analyzed_at": repo.analyzed_at,
                "statistics": {
                    "total_resources": repo.total_resources,
                    "total_modules": repo.total_modules,
                    "total_variables": repo.total_variables,
                    "total_outputs": repo.total_outputs,
                    "providers_count": repo.providers_count
                }
            }
            for repo in repositories
        ]
    }

# Made with Bob
