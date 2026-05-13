import os
from typing import Dict, List, Optional
from git import Repo
from pathlib import Path


class RepositoryManager:
    """Manage GitHub repository cloning and local caching"""
    
    def __init__(self, workspace_dir: str = "./cloned_repos"):
        self.workspace_dir = workspace_dir
        os.makedirs(workspace_dir, exist_ok=True)
    
    def extract_repo_info(self, url: str) -> Dict[str, str]:
        """
        Extract repository owner and name from GitHub URL
        Supports formats:
        - https://github.com/owner/repo
        - https://github.com/owner/repo.git
        - git@github.com:owner/repo
        - git@github.com:owner/repo.git
        """
        # Clean URL
        url = url.strip().rstrip('/')
        
        if url.endswith('.git'):
            url = url[:-4]
        
        # Extract from HTTPS
        if 'github.com/' in url:
            parts = url.split('github.com/')[-1].split('/')
            if len(parts) >= 2:
                return {
                    'owner': parts[0],
                    'name': parts[1],
                    'url': url if url.startswith('http') else f"https://github.com/{parts[0]}/{parts[1]}"
                }
        
        # Extract from SSH
        if 'github.com:' in url:
            parts = url.split('github.com:')[-1].split('/')
            if len(parts) >= 2:
                return {
                    'owner': parts[0],
                    'name': parts[1],
                    'url': f"https://github.com/{parts[0]}/{parts[1]}"
                }
        
        raise ValueError(f"Invalid GitHub URL: {url}")
    
    def get_local_path(self, owner: str, repo_name: str) -> str:
        """Get local filesystem path for cloned repository"""
        return os.path.join(self.workspace_dir, owner, repo_name)
    
    def clone_repository(self, url: str, branch: str = "main") -> str:
        """
        Clone repository from GitHub to local workspace
        Returns: path to cloned repository
        """
        try:
            repo_info = self.extract_repo_info(url)
            local_path = self.get_local_path(repo_info['owner'], repo_info['name'])
            
            # Create parent directory
            os.makedirs(os.path.dirname(local_path), exist_ok=True)
            
            # Clone if not exists
            if not os.path.exists(local_path):
                repo = Repo.clone_from(
                    repo_info['url'],
                    local_path,
                    branch=branch,
                    depth=1  # Shallow clone for faster download
                )
            else:
                # Update existing repository
                repo = Repo(local_path)
                repo.heads[branch].checkout()
                repo.remotes.origin.pull()
            
            return local_path
        
        except Exception as e:
            raise RuntimeError(f"Failed to clone repository: {str(e)}")
    
    def setup_directories(self, local_path: str) -> None:
        """Ensure necessary directories exist in workspace"""
        os.makedirs(local_path, exist_ok=True)
    
    def get_repository_size_mb(self, local_path: str) -> float:
        """Calculate repository size in MB"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(local_path):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                if os.path.exists(filepath):
                    total_size += os.path.getsize(filepath)
        return total_size / (1024 * 1024)
    
    def cleanup_repository(self, local_path: str) -> None:
        """Remove cloned repository from workspace"""
        try:
            import shutil
            if os.path.exists(local_path):
                shutil.rmtree(local_path)
        except Exception as e:
            raise RuntimeError(f"Failed to cleanup repository: {str(e)}")
