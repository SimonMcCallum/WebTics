"""
WebTics middleware package.
Security and validation middleware for the FastAPI application.
"""

from .data_validation import validation_middleware

__all__ = ["validation_middleware"]
