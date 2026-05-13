"""GitHub Repository Ingestion Service

Handles repository URL validation, cloning, metadata extraction, and cleanup.
"""

import os
import shutil
import re
from typing import Dict, Optional, Tuple
from pathlib import Path
from git import Repo, GitCommandError
from config.logger import logger


class RepositoryValidationError(Exception):
    """Raised when repository validation fails"""
    pass


class RepositoryIngestionError(Exception):
    """Raised when repository ingestion fails"""
    pass


class RepoIngestionService:
    """Service for ingesting GitHub repositories"""
    
    GITHUB_URL_PATTERNS = (
        r'^https://github\.com/[\w-]+/[\w.-]+(?:\.git)?/?$',  # HTTPS
        r'^git@github\.com:[\w-]+/[\w.-]+(?:\.git)?/?$',       # SSH
    )
    
    def __init__(self, workspace_dir: str = "./cloned_repos"):
        """
        Initialize the ingestion service
        
        Args:
            workspace_dir: Root directory for cloned repositories
        """
        self.workspace_dir = Path(workspace_dir)
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Initialized RepoIngestionService with workspace: {self.workspace_dir}")
    
    # ===== URL Validation =====
    
    def validate_github_url(self, url: str) -> bool:
        """
        Validate if URL is a valid GitHub repository URL
        
        Args:
            url: Repository URL to validate
            
        Returns:
            True if valid, False otherwise
        """
        url = url.strip()
        return any(re.match(pattern, url) for pattern in self.GITHUB_URL_PATTERNS)
    
    def parse_github_url(self, url: str) -> Dict[str, str]:
        """
        Parse GitHub URL and extract owner/repo information
        
        Args:
            url: GitHub repository URL
            
        Returns:
            Dictionary with owner, name, and normalized URL
            
        Raises:
            RepositoryValidationError: If URL format is invalid
        """
        if not self.validate_github_url(url):
            raise RepositoryValidationError(
                f"Invalid GitHub URL format: {url}. "
                "Expected: https://github.com/owner/repo or git@github.com:owner/repo"
            )
        
        url = url.strip().rstrip('/').rstrip('.git')
        
        # Extract from HTTPS URLs
        if url.startswith('https://'):
            try:
                parts = url.replace('https://github.com/', '').split('/')
                if len(parts) < 2:
                    raise RepositoryValidationError(f"Invalid GitHub URL: {url}")
                owner, repo = parts[0], parts[1]
            except (IndexError, ValueError) as e:
                raise RepositoryValidationError(f"Cannot parse GitHub URL: {url}") from e
        
        # Extract from SSH URLs
        elif url.startswith('git@'):
            try:
                parts = url.replace('git@github.com:', '').split('/')
                if len(parts) < 2:
                    raise RepositoryValidationError(f"Invalid GitHub URL: {url}")
                owner, repo = parts[0], parts[1]
            except (IndexError, ValueError) as e:
                raise RepositoryValidationError(f"Cannot parse GitHub URL: {url}") from e
        
        else:
            raise RepositoryValidationError(f"Unsupported GitHub URL format: {url}")
        
        # Validate owner and repo names
        if not re.match(r'^[\w-]+$', owner) or not re.match(r'^[\w.-]+$', repo):
            raise RepositoryValidationError(f"Invalid repository owner or name: {owner}/{repo}")
        
        # Clean repo name (remove .git if present)
        repo = repo.replace('.git', '')
        
        # Normalize URL to HTTPS format
        normalized_url = f"https://github.com/{owner}/{repo}"
        
        return {
            'owner': owner,
            'name': repo,
            'url': normalized_url,
            'clone_url': url if url.startswith('https://') or url.startswith('git@') else normalized_url + '.git'
        }
    
    # ===== Repository Cloning =====
    
    def get_local_path(self, owner: str, repo: str) -> Path:
        """
        Get local filesystem path for a repository
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            Path object for repository
        """
        return self.workspace_dir / owner / repo
    
    def repository_exists(self, owner: str, repo: str) -> bool:
        """
        Check if repository is already cloned locally
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            True if repository exists, False otherwise
        """
        local_path = self.get_local_path(owner, repo)
        return local_path.exists() and (local_path / '.git').exists()
    
    def clone_repository(
        self, 
        url: str, 
        branch: str = "main",
        force_refresh: bool = False
    ) -> Dict[str, any]:
        """
        Clone a GitHub repository locally
        
        Args:
            url: GitHub repository URL
            branch: Git branch to clone (default: main)
            force_refresh: Delete and re-clone if already exists
            
        Returns:
            Dictionary with repository metadata
            
        Raises:
            RepositoryValidationError: If URL is invalid
            RepositoryIngestionError: If cloning fails
        """
        try:
            # Parse and validate URL
            repo_info = self.parse_github_url(url)
            owner = repo_info['owner']
            name = repo_info['name']
            clone_url = repo_info['clone_url']
            
            local_path = self.get_local_path(owner, name)
            
            # Handle existing repository
            if local_path.exists():
                if force_refresh:
                    logger.info(f"Removing existing repository: {local_path}")
                    shutil.rmtree(local_path)
                else:
                    # Try to fetch latest from remote
                    try:
                        logger.info(f"Repository already exists, updating: {local_path}")
                        git_repo = Repo(str(local_path))
                        git_repo.remotes.origin.fetch()
                        git_repo.heads[branch].checkout()
                        git_repo.remotes.origin.pull(branch)
                        return self._get_repo_metadata(git_repo, owner, name)
                    except Exception as e:
                        logger.warning(f"Failed to update existing repo, will re-clone: {e}")
                        shutil.rmtree(local_path)
            
            # Create parent directory
            local_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Clone with shallow copy to save bandwidth
            logger.info(f"Cloning repository from {clone_url} to {local_path}")
            git_repo = Repo.clone_from(
                clone_url,
                str(local_path),
                branch=branch,
                depth=1,  # Shallow clone
                single_branch=True
            )
            
            logger.info(f"Successfully cloned: {owner}/{name} at {local_path}")
            return self._get_repo_metadata(git_repo, owner, name)
        
        except RepositoryValidationError:
            raise
        except GitCommandError as e:
            error_msg = f"Git error while cloning {url}: {str(e)}"
            logger.error(error_msg)
            raise RepositoryIngestionError(error_msg) from e
        except Exception as e:
            error_msg = f"Failed to clone repository {url}: {str(e)}"
            logger.error(error_msg)
            raise RepositoryIngestionError(error_msg) from e
    
    def _get_repo_metadata(self, git_repo: Repo, owner: str, name: str) -> Dict[str, any]:
        """
        Extract metadata from a cloned repository
        
        Args:
            git_repo: GitPython Repo object
            owner: Repository owner
            name: Repository name
            
        Returns:
            Dictionary with repository metadata
        """
        try:
            commit_count = int(git_repo.git.rev_list('--count', 'HEAD'))
            latest_commit = git_repo.head.commit
            
            return {
                'owner': owner,
                'name': name,
                'url': f"https://github.com/{owner}/{name}",
                'local_path': str(self.get_local_path(owner, name)),
                'branch': git_repo.active_branch.name,
                'commit_hash': latest_commit.hexsha[:8],
                'commit_message': latest_commit.message.strip(),
                'commit_author': str(latest_commit.author),
                'commit_date': str(latest_commit.committed_datetime),
                'total_commits': commit_count,
                'is_cloned': True
            }
        except Exception as e:
            logger.warning(f"Failed to extract full metadata: {e}")
            return {
                'owner': owner,
                'name': name,
                'url': f"https://github.com/{owner}/{name}",
                'local_path': str(self.get_local_path(owner, name)),
                'branch': 'unknown',
                'is_cloned': True
            }
    
    # ===== Repository Scanning =====
    
    def find_terraform_files(self, owner: str, repo: str) -> list:
        """
        Recursively find all Terraform files in cloned repository
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            List of Terraform file paths (relative to repo root)
            
        Raises:
            RepositoryIngestionError: If repository not found
        """
        repo_path = self.get_local_path(owner, repo)
        
        if not repo_path.exists():
            raise RepositoryIngestionError(f"Repository not found at {repo_path}")
        
        terraform_files = []
        exclude_dirs = {'.terraform', '.git', '.gitignore', 'node_modules', '.venv'}
        
        try:
            for root, dirs, files in os.walk(repo_path):
                # Remove excluded directories from traversal
                dirs[:] = [d for d in dirs if d not in exclude_dirs]
                
                for file in files:
                    if file.endswith(('.tf', '.tfvars')):
                        file_path = Path(root) / file
                        relative_path = file_path.relative_to(repo_path)
                        terraform_files.append(str(relative_path))
            
            logger.info(f"Found {len(terraform_files)} Terraform files in {owner}/{repo}")
            return sorted(terraform_files)
        
        except Exception as e:
            error_msg = f"Failed to scan Terraform files: {e}"
            logger.error(error_msg)
            raise RepositoryIngestionError(error_msg) from e
    
    def get_terraform_file_content(self, owner: str, repo: str, file_path: str) -> Tuple[str, str]:
        """
        Read content of a Terraform file
        
        Args:
            owner: Repository owner
            repo: Repository name
            file_path: Relative path to file
            
        Returns:
            Tuple of (file_path, content)
            
        Raises:
            RepositoryIngestionError: If file cannot be read
        """
        repo_path = self.get_local_path(owner, repo)
        full_path = repo_path / file_path
        
        if not full_path.exists():
            raise RepositoryIngestionError(f"File not found: {file_path}")
        
        if not str(full_path).startswith(str(repo_path)):
            raise RepositoryIngestionError(f"Path traversal attempt detected: {file_path}")
        
        try:
            with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
            return (file_path, content)
        except Exception as e:
            error_msg = f"Failed to read file {file_path}: {e}"
            logger.error(error_msg)
            raise RepositoryIngestionError(error_msg) from e
    
    # ===== Cleanup =====
    
    def delete_repository(self, owner: str, repo: str) -> bool:
        """
        Delete a cloned repository from local storage
        
        Args:
            owner: Repository owner
            repo: Repository name
            
        Returns:
            True if deleted successfully, False if not found
        """
        repo_path = self.get_local_path(owner, repo)
        
        if not repo_path.exists():
            logger.warning(f"Repository not found, cannot delete: {repo_path}")
            return False
        
        try:
            logger.info(f"Deleting repository: {repo_path}")
            shutil.rmtree(repo_path)
            logger.info(f"Successfully deleted repository: {owner}/{repo}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete repository {owner}/{repo}: {e}")
            raise RepositoryIngestionError(f"Failed to delete repository: {e}") from e
    
    def cleanup_old_repositories(self, max_age_days: int = 30) -> Dict[str, int]:
        """
        Clean up repositories older than specified age
        
        Args:
            max_age_days: Maximum age in days
            
        Returns:
            Dictionary with cleanup statistics
        """
        import time
        
        stats = {'checked': 0, 'deleted': 0, 'errors': 0}
        current_time = time.time()
        max_age_seconds = max_age_days * 24 * 60 * 60
        
        try:
            for owner_dir in self.workspace_dir.iterdir():
                if not owner_dir.is_dir():
                    continue
                
                for repo_dir in owner_dir.iterdir():
                    if not repo_dir.is_dir():
                        continue
                    
                    stats['checked'] += 1
                    mod_time = os.path.getmtime(repo_dir)
                    age_seconds = current_time - mod_time
                    
                    if age_seconds > max_age_seconds:
                        try:
                            shutil.rmtree(repo_dir)
                            stats['deleted'] += 1
                            logger.info(f"Cleaned up old repository: {owner_dir.name}/{repo_dir.name}")
                        except Exception as e:
                            stats['errors'] += 1
                            logger.error(f"Failed to cleanup {owner_dir.name}/{repo_dir.name}: {e}")
        
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
        
        logger.info(f"Cleanup complete: {stats}")
        return stats
    
    def get_storage_usage(self) -> Dict[str, any]:
        """
        Calculate total storage usage for cloned repositories
        
        Returns:
            Dictionary with storage statistics
        """
        def get_size(path: Path) -> int:
            """Calculate total size of directory"""
            total = 0
            for entry in path.rglob('*'):
                if entry.is_file():
                    try:
                        total += entry.stat().st_size
                    except OSError:
                        pass
            return total
        
        if not self.workspace_dir.exists():
            return {'total_bytes': 0, 'total_mb': 0, 'repositories': 0}
        
        total_size = get_size(self.workspace_dir)
        
        repo_count = sum(
            1 for owner_dir in self.workspace_dir.iterdir()
            if owner_dir.is_dir()
            for repo_dir in owner_dir.iterdir()
            if repo_dir.is_dir() and (repo_dir / '.git').exists()
        )
        
        return {
            'total_bytes': total_size,
            'total_mb': round(total_size / (1024 * 1024), 2),
            'repositories': repo_count
        }
