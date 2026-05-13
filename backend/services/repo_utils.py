"""Repository utility functions

Collection of utility functions for repository validation, cleanup, and management.
"""

import os
from datetime import datetime, timedelta
from typing import List, Dict
from pathlib import Path


def validate_repo_name(name: str) -> bool:
    """
    Validate repository name format
    
    Args:
        name: Repository name
        
    Returns:
        True if valid, False otherwise
    """
    import re
    # Repository names can contain alphanumeric, hyphens, underscores, periods
    return bool(re.match(r'^[\w.-]+$', name)) and 1 <= len(name) <= 255


def validate_owner_name(owner: str) -> bool:
    """
    Validate repository owner name format
    
    Args:
        owner: Owner/organization name
        
    Returns:
        True if valid, False otherwise
    """
    import re
    # Owner names can contain alphanumeric, hyphens
    return bool(re.match(r'^[\w-]+$', owner)) and 1 <= len(owner) <= 39


def normalize_url(url: str) -> str:
    """
    Normalize GitHub URL to HTTPS format
    
    Args:
        url: GitHub repository URL
        
    Returns:
        Normalized URL
    """
    url = url.strip().rstrip('/')
    
    if url.endswith('.git'):
        url = url[:-4]
    
    # Convert SSH to HTTPS
    if url.startswith('git@github.com:'):
        url = url.replace('git@github.com:', 'https://github.com/')
    
    # Ensure HTTPS
    if not url.startswith('https://'):
        url = 'https://' + url.lstrip('http://')
    
    return url


def get_age_in_days(file_path: Path) -> int:
    """
    Calculate age of a file/directory in days
    
    Args:
        file_path: Path to file or directory
        
    Returns:
        Age in days
    """
    if not file_path.exists():
        return 0
    
    mod_time = os.path.getmtime(file_path)
    mod_date = datetime.fromtimestamp(mod_time)
    age = datetime.now() - mod_date
    return age.days


def format_bytes(bytes_size: int) -> str:
    """
    Format bytes to human-readable format
    
    Args:
        bytes_size: Size in bytes
        
    Returns:
        Formatted string (B, KB, MB, GB, TB)
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.2f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.2f} PB"


def get_directory_size(path: Path) -> int:
    """
    Calculate total size of directory
    
    Args:
        path: Directory path
        
    Returns:
        Size in bytes
    """
    total_size = 0
    
    try:
        for entry in path.rglob('*'):
            if entry.is_file():
                try:
                    total_size += entry.stat().st_size
                except OSError:
                    pass
    except Exception:
        pass
    
    return total_size


def cleanup_empty_directories(root_path: Path) -> int:
    """
    Remove empty directories recursively
    
    Args:
        root_path: Root path to traverse
        
    Returns:
        Number of directories removed
    """
    removed_count = 0
    
    try:
        for dirpath, dirnames, filenames in os.walk(root_path, topdown=False):
            if not dirnames and not filenames:
                try:
                    os.rmdir(dirpath)
                    removed_count += 1
                except OSError:
                    pass
    except Exception:
        pass
    
    return removed_count


class StorageQuotaManager:
    """Manage storage quota for repositories"""
    
    def __init__(self, max_size_gb: int = 10):
        """
        Initialize storage quota manager
        
        Args:
            max_size_gb: Maximum storage size in GB
        """
        self.max_size_bytes = max_size_gb * 1024 * 1024 * 1024
    
    def get_current_usage(self, repos_dir: Path) -> int:
        """Get current storage usage in bytes"""
        return get_directory_size(repos_dir)
    
    def has_quota_exceeded(self, repos_dir: Path) -> bool:
        """Check if storage quota is exceeded"""
        return self.get_current_usage(repos_dir) > self.max_size_bytes
    
    def get_available_space(self, repos_dir: Path) -> int:
        """Get available space in bytes"""
        usage = self.get_current_usage(repos_dir)
        available = self.max_size_bytes - usage
        return max(0, available)


class RepositoryIndexer:
    """Index local repositories for quick lookup"""
    
    def __init__(self, root_dir: Path):
        """
        Initialize indexer
        
        Args:
            root_dir: Root directory containing repositories
        """
        self.root_dir = Path(root_dir)
    
    def list_all_repositories(self) -> List[Dict[str, str]]:
        """
        List all cloned repositories
        
        Returns:
            List of repository info dictionaries
        """
        repos = []
        
        try:
            for owner_dir in self.root_dir.iterdir():
                if not owner_dir.is_dir():
                    continue
                
                for repo_dir in owner_dir.iterdir():
                    if not repo_dir.is_dir():
                        continue
                    
                    if (repo_dir / '.git').exists():
                        repos.append({
                            'owner': owner_dir.name,
                            'name': repo_dir.name,
                            'path': str(repo_dir),
                            'size_mb': round(get_directory_size(repo_dir) / (1024 * 1024), 2),
                            'age_days': get_age_in_days(repo_dir)
                        })
        except Exception:
            pass
        
        return repos
    
    def find_repositories_by_owner(self, owner: str) -> List[Dict[str, str]]:
        """
        Find all repositories by owner
        
        Args:
            owner: Repository owner
            
        Returns:
            List of repository info dictionaries
        """
        repos = []
        owner_dir = self.root_dir / owner
        
        if not owner_dir.exists():
            return repos
        
        try:
            for repo_dir in owner_dir.iterdir():
                if repo_dir.is_dir() and (repo_dir / '.git').exists():
                    repos.append({
                        'owner': owner,
                        'name': repo_dir.name,
                        'path': str(repo_dir),
                        'size_mb': round(get_directory_size(repo_dir) / (1024 * 1024), 2),
                        'age_days': get_age_in_days(repo_dir)
                    })
        except Exception:
            pass
        
        return repos
