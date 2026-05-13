import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # Database
    database_url: str = "postgresql://ikg_user:ikg_password@localhost:5432/ikg_db"
    
    # Environment
    environment: str = "development"
    debug: bool = True
    log_level: str = "INFO"
    
    # Application
    app_name: str = "Infra Knowledge Graph"
    api_prefix: str = "/api"
    
    # Terraform parsing
    tf_workspace_dir: str = "./cloned_repos"
    max_repo_size_mb: int = 500
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
