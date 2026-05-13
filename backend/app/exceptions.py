"""
Custom exceptions for the application
"""


class AnalysisException(Exception):
    """Base exception for analysis errors"""
    pass


class RepositoryNotFound(AnalysisException):
    """Repository not found"""
    pass


class RepositoryCloneException(AnalysisException):
    """Error cloning repository"""
    pass


class ParsingException(AnalysisException):
    """Error parsing Terraform files"""
    pass


class GraphBuildException(AnalysisException):
    """Error building dependency graph"""
    pass
