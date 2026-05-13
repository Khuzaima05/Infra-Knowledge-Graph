"""Typed schemas for Terraform parser output

Pydantic models for structured, type-safe parser results.
"""

from typing import List, Dict, Any, Optional, Literal
from pydantic import BaseModel, Field


class ParsedResource(BaseModel):
    """Parsed Terraform resource"""
    type: str = Field(..., description="Resource type (e.g., aws_vpc)")
    name: str = Field(..., description="Resource name")
    full_name: str = Field(..., description="Full resource identifier (type.name)")
    provider: str = Field(..., description="Provider name extracted from type")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Resource configuration")
    file_path: Optional[str] = Field(None, description="Source file path")
    line_number: Optional[int] = Field(None, description="Line number in source file")


class ParsedModule(BaseModel):
    """Parsed Terraform module"""
    name: str = Field(..., description="Module name")
    source: str = Field(..., description="Module source path or URL")
    version: Optional[str] = Field(None, description="Module version constraint")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Module configuration")
    file_path: Optional[str] = Field(None, description="Source file path")
    line_number: Optional[int] = Field(None, description="Line number in source file")


class ParsedVariable(BaseModel):
    """Parsed Terraform variable"""
    name: str = Field(..., description="Variable name")
    type: str = Field(default="string", description="Variable type")
    default_value: Optional[Any] = Field(None, description="Default value")
    description: str = Field(default="", description="Variable description")
    sensitive: bool = Field(default=False, description="Whether variable is sensitive")
    validation: Optional[Dict[str, Any]] = Field(None, description="Validation rules")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    file_path: Optional[str] = Field(None, description="Source file path")
    line_number: Optional[int] = Field(None, description="Line number in source file")


class ParsedOutput(BaseModel):
    """Parsed Terraform output"""
    name: str = Field(..., description="Output name")
    value: Optional[Any] = Field(None, description="Output value expression")
    description: str = Field(default="", description="Output description")
    sensitive: bool = Field(default=False, description="Whether output is sensitive")
    depends_on: List[str] = Field(default_factory=list, description="Dependencies")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    file_path: Optional[str] = Field(None, description="Source file path")
    line_number: Optional[int] = Field(None, description="Line number in source file")


class ParsedProvider(BaseModel):
    """Parsed Terraform provider"""
    name: str = Field(..., description="Provider name")
    version: Optional[str] = Field(None, description="Provider version constraint")
    alias: Optional[str] = Field(None, description="Provider alias")
    source: Optional[str] = Field(None, description="Provider source")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Provider configuration")
    file_path: Optional[str] = Field(None, description="Source file path")
    line_number: Optional[int] = Field(None, description="Line number in source file")


class ParsedLocal(BaseModel):
    """Parsed Terraform local value"""
    name: str = Field(..., description="Local value name")
    value: Any = Field(..., description="Local value expression")
    file_path: Optional[str] = Field(None, description="Source file path")
    line_number: Optional[int] = Field(None, description="Line number in source file")


class ParsedDataSource(BaseModel):
    """Parsed Terraform data source"""
    type: str = Field(..., description="Data source type")
    name: str = Field(..., description="Data source name")
    full_name: str = Field(..., description="Full identifier (data.type.name)")
    provider: str = Field(..., description="Provider name")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Data source configuration")
    file_path: Optional[str] = Field(None, description="Source file path")
    line_number: Optional[int] = Field(None, description="Line number in source file")


class ParsedReference(BaseModel):
    """Detected reference in Terraform code"""
    type: Literal["variable", "module_output", "resource_attribute", "local", "data_source"] = Field(
        ..., description="Reference type"
    )
    target: Optional[str] = Field(None, description="Target identifier")
    source_file: Optional[str] = Field(None, description="File containing reference")
    context: Optional[str] = Field(None, description="Context where reference appears")


class FileParseResult(BaseModel):
    """Result of parsing a single file"""
    file_path: str = Field(..., description="Relative file path")
    status: Literal["success", "error", "warning"] = Field(..., description="Parse status")
    error: Optional[str] = Field(None, description="Error message if parsing failed")
    resources: List[ParsedResource] = Field(default_factory=list)
    modules: List[ParsedModule] = Field(default_factory=list)
    variables: List[ParsedVariable] = Field(default_factory=list)
    outputs: List[ParsedOutput] = Field(default_factory=list)
    providers: List[ParsedProvider] = Field(default_factory=list)
    locals: List[ParsedLocal] = Field(default_factory=list)
    data_sources: List[ParsedDataSource] = Field(default_factory=list)
    references: List[ParsedReference] = Field(default_factory=list)


class RepositoryParseResult(BaseModel):
    """Complete result of parsing a repository"""
    status: Literal["success", "partial", "error"] = Field(..., description="Overall parse status")
    total_files: int = Field(default=0, description="Total Terraform files found")
    parsed_files: int = Field(default=0, description="Successfully parsed files")
    failed_files: int = Field(default=0, description="Failed to parse files")
    
    # Aggregated components
    resources: List[ParsedResource] = Field(default_factory=list)
    modules: List[ParsedModule] = Field(default_factory=list)
    variables: List[ParsedVariable] = Field(default_factory=list)
    outputs: List[ParsedOutput] = Field(default_factory=list)
    providers: List[ParsedProvider] = Field(default_factory=list)
    locals: List[ParsedLocal] = Field(default_factory=list)
    data_sources: List[ParsedDataSource] = Field(default_factory=list)
    references: List[ParsedReference] = Field(default_factory=list)
    
    # File-level results
    file_results: List[FileParseResult] = Field(default_factory=list)
    errors: List[str] = Field(default_factory=list, description="All parsing errors")
    
    # Statistics
    statistics: Dict[str, int] = Field(
        default_factory=lambda: {
            "total_resources": 0,
            "total_modules": 0,
            "total_variables": 0,
            "total_outputs": 0,
            "total_providers": 0,
            "total_locals": 0,
            "total_data_sources": 0,
            "total_references": 0
        }
    )
    
    def update_statistics(self):
        """Update statistics based on parsed components"""
        self.statistics = {
            "total_resources": len(self.resources),
            "total_modules": len(self.modules),
            "total_variables": len(self.variables),
            "total_outputs": len(self.outputs),
            "total_providers": len(self.providers),
            "total_locals": len(self.locals),
            "total_data_sources": len(self.data_sources),
            "total_references": len(self.references)
        }


class ParserConfig(BaseModel):
    """Configuration for Terraform parser"""
    exclude_dirs: List[str] = Field(
        default_factory=lambda: ['.terraform', '.git', 'node_modules', '.venv', '__pycache__'],
        description="Directories to exclude from scanning"
    )
    file_extensions: List[str] = Field(
        default_factory=lambda: ['.tf', '.tfvars'],
        description="File extensions to parse"
    )
    max_file_size_mb: int = Field(default=10, description="Maximum file size to parse (MB)")
    continue_on_error: bool = Field(default=True, description="Continue parsing on file errors")
    extract_references: bool = Field(default=True, description="Extract variable/resource references")
    normalize_values: bool = Field(default=True, description="Normalize parsed values")

# Made with Bob
