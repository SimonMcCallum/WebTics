"""
Security middleware for WebTics.
Implements security headers and HTTPS enforcement.
"""

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import RedirectResponse
import os


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # Only add HSTS if using HTTPS (or in production)
        if request.url.scheme == "https" or os.getenv("ENVIRONMENT") == "production":
            # HSTS: Force HTTPS for 1 year
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # XSS protection
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Referrer policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Content Security Policy (basic - adjust for your needs)
        response.headers["Content-Security-Policy"] = "default-src 'self'"

        # Permissions Policy (formerly Feature-Policy)
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"

        return response


async def https_redirect_middleware(request: Request, call_next):
    """Redirect HTTP to HTTPS in production."""

    # Only enforce HTTPS redirect in production
    if os.getenv("ENVIRONMENT") == "production":
        if request.url.scheme != "https":
            # Redirect to HTTPS
            https_url = str(request.url).replace("http://", "https://", 1)
            return RedirectResponse(url=https_url, status_code=301)

    response = await call_next(request)
    return response
