# Middleware for error handling
from fastapi import Request, status
from fastapi.responses import JSONResponse
from app.exceptions import AnalysisException
from config.logger import logger


async def exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    
    if isinstance(exc, AnalysisException):
        logger.warning(f"Analysis error: {str(exc)}")
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc)}
        )
    
    logger.error(f"Unexpected error: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )
