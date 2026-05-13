from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON, Boolean, Float, Table
from sqlalchemy.orm import relationship
from models.database import Base

# Association table for many-to-many relationships
module_variables = Table(
    'module_variables',
    Base.metadata,
    Column('module_id', Integer, ForeignKey('modules.id'), primary_key=True),
    Column('variable_id', Integer, ForeignKey('variables.id'), primary_key=True)
)


class Repository(Base):
    """Terraform repository metadata"""
    __tablename__ = "repositories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    url = Column(String(255), unique=True, nullable=False)
    branch = Column(String(255), default="main")
    cloned_path = Column(String(500), nullable=True)
    
    # Statistics
    total_resources = Column(Integer, default=0)
    total_modules = Column(Integer, default=0)
    total_variables = Column(Integer, default=0)
    total_outputs = Column(Integer, default=0)
    providers_count = Column(Integer, default=0)
    
    # Status
    status = Column(String(50), default="pending")  # pending, analyzing, completed, failed
    error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    analyzed_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    terraform_files = relationship("TerraformFile", back_populates="repository", cascade="all, delete-orphan")
    graph = relationship("Graph", back_populates="repository", uselist=False, cascade="all, delete-orphan")
    summary = relationship("Summary", back_populates="repository", uselist=False, cascade="all, delete-orphan")


class TerraformFile(Base):
    """Individual Terraform files in a repository"""
    __tablename__ = "terraform_files"
    
    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(Integer, ForeignKey("repositories.id"), nullable=False)
    file_path = Column(String(500), nullable=False)
    content = Column(Text, nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    repository = relationship("Repository", back_populates="terraform_files")
    modules = relationship("Module", back_populates="terraform_file", cascade="all, delete-orphan")
    resources = relationship("Resource", back_populates="terraform_file", cascade="all, delete-orphan")
    variables = relationship("Variable", back_populates="terraform_file", cascade="all, delete-orphan")


class Module(Base):
    """Terraform modules"""
    __tablename__ = "modules"
    
    id = Column(Integer, primary_key=True, index=True)
    terraform_file_id = Column(Integer, ForeignKey("terraform_files.id"), nullable=False)
    repository_id = Column(Integer, ForeignKey("repositories.id"), nullable=False)
    
    name = Column(String(255), nullable=False)
    source = Column(String(500), nullable=True)
    version = Column(String(50), nullable=True)
    
    # Module metadata as JSON
    metadata = Column(JSON, default={})
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    terraform_file = relationship("TerraformFile", back_populates="modules")
    repository = relationship("Repository")
    variables = relationship("Variable", secondary="module_variables", back_populates="modules")


class Resource(Base):
    """Terraform resources"""
    __tablename__ = "resources"
    
    id = Column(Integer, primary_key=True, index=True)
    terraform_file_id = Column(Integer, ForeignKey("terraform_files.id"), nullable=False)
    repository_id = Column(Integer, ForeignKey("repositories.id"), nullable=False)
    
    type = Column(String(255), nullable=False)  # e.g., aws_vpc, aws_subnet
    name = Column(String(255), nullable=False)  # e.g., main, primary
    full_name = Column(String(500), nullable=False)  # e.g., aws_vpc.main
    
    provider = Column(String(100), nullable=True)  # e.g., aws, gcp, azure
    metadata = Column(JSON, default={})
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    terraform_file = relationship("TerraformFile", back_populates="resources")
    repository = relationship("Repository")


class Variable(Base):
    """Terraform variables"""
    __tablename__ = "variables"
    
    id = Column(Integer, primary_key=True, index=True)
    terraform_file_id = Column(Integer, ForeignKey("terraform_files.id"), nullable=False)
    repository_id = Column(Integer, ForeignKey("repositories.id"), nullable=False)
    
    name = Column(String(255), nullable=False)
    type = Column(String(100), nullable=True)  # string, number, bool, list, map, etc.
    default_value = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    
    metadata = Column(JSON, default={})
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    terraform_file = relationship("TerraformFile", back_populates="variables")
    repository = relationship("Repository")
    modules = relationship("Module", secondary="module_variables", back_populates="variables")


class Output(Base):
    """Terraform outputs"""
    __tablename__ = "outputs"
    
    id = Column(Integer, primary_key=True, index=True)
    terraform_file_id = Column(Integer, ForeignKey("terraform_files.id"), nullable=False)
    repository_id = Column(Integer, ForeignKey("repositories.id"), nullable=False)
    
    name = Column(String(255), nullable=False)
    value = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    
    metadata = Column(JSON, default={})
    
    created_at = Column(DateTime, default=datetime.utcnow)


class Provider(Base):
    """Terraform providers"""
    __tablename__ = "providers"
    
    id = Column(Integer, primary_key=True, index=True)
    terraform_file_id = Column(Integer, ForeignKey("terraform_files.id"), nullable=False)
    repository_id = Column(Integer, ForeignKey("repositories.id"), nullable=False)
    
    name = Column(String(100), nullable=False)  # aws, gcp, azure, kubernetes, etc.
    version = Column(String(50), nullable=True)
    alias = Column(String(100), nullable=True)
    
    metadata = Column(JSON, default={})
    
    created_at = Column(DateTime, default=datetime.utcnow)


class Relationship(Base):
    """Dependencies and relationships between Terraform objects"""
    __tablename__ = "relationships"
    
    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(Integer, ForeignKey("repositories.id"), nullable=False)
    
    source_type = Column(String(50), nullable=False)  # module, resource, variable, output, provider
    source_id = Column(String(255), nullable=False)  # e.g., aws_vpc.main
    
    target_type = Column(String(50), nullable=False)
    target_id = Column(String(255), nullable=False)
    
    relationship_type = Column(String(100), nullable=False)  # references, uses, depends_on, etc.
    
    metadata = Column(JSON, default={})
    
    created_at = Column(DateTime, default=datetime.utcnow)


class Graph(Base):
    """Pre-computed graph for visualization"""
    __tablename__ = "graphs"
    
    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(Integer, ForeignKey("repositories.id"), unique=True, nullable=False)
    
    # Graph data
    nodes = Column(JSON, nullable=False)  # Array of nodes
    edges = Column(JSON, nullable=False)  # Array of edges
    graph_type = Column(String(50), default="dependency")  # dependency, module_lineage, variable_map
    
    # Statistics
    node_count = Column(Integer, default=0)
    edge_count = Column(Integer, default=0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    repository = relationship("Repository", back_populates="graph")


class Summary(Base):
    """AI-generated architecture summary"""
    __tablename__ = "summaries"
    
    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(Integer, ForeignKey("repositories.id"), unique=True, nullable=False)
    
    title = Column(String(255), nullable=False)
    architecture_description = Column(Text, nullable=False)
    key_components = Column(JSON, default=[])  # Array of {name, description}
    deployment_overview = Column(Text, nullable=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    repository = relationship("Repository", back_populates="summary")
