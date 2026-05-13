"""
Utility functions for the application
"""

import os
import shutil
from pathlib import Path


def ensure_directory_exists(directory_path: str) -> None:
    """Ensure directory exists, create if not"""
    Path(directory_path).mkdir(parents=True, exist_ok=True)


def get_directory_size_mb(directory_path: str) -> float:
    """Calculate total directory size in MB"""
    total_size = 0
    for dirpath, dirnames, filenames in os.walk(directory_path):
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            if os.path.exists(filepath):
                total_size += os.path.getsize(filepath)
    return total_size / (1024 * 1024)


def remove_directory(directory_path: str) -> None:
    """Remove directory and all contents"""
    if os.path.exists(directory_path):
        shutil.rmtree(directory_path)


def sanitize_repository_name(name: str) -> str:
    """Sanitize repository name for filesystem safety"""
    # Replace unsafe characters with underscores
    unsafe_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in unsafe_chars:
        name = name.replace(char, '_')
    return name


def is_terraform_file(filename: str) -> bool:
    """Check if file is a Terraform file"""
    return filename.endswith('.tf')
