"""
API authentication middleware for WebTics.
Implements API key authentication and rate limiting.
"""

from fastapi import HTTPException, Request, status
from fastapi.security import APIKeyHeader
from datetime import datetime, timedelta
import hashlib
import os
import logging
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)
security_logger = logging.getLogger("webtics.security")

# API Key header
API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

# Valid API keys (hashed for security)
# In production, store these in a database with proper hashing
def get_valid_api_keys() -> Dict[str, str]:
    """Get valid API keys from environment."""
    api_key = os.getenv("WEBTICS_API_KEY", "")
    if not api_key:
        logger.warning("No WEBTICS_API_KEY set in environment!")
        return {}

    # Hash the API key for comparison (SHA-256)
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    return {key_hash: "default_client"}


# Rate limiting configuration
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX = 100  # requests per window
RATE_LIMIT_BURST = 120  # burst allowance

# In-memory rate limit tracking (use Redis in production for distributed systems)
class RateLimiter:
    """Simple in-memory rate limiter."""

    def __init__(self):
        self.requests: Dict[str, List[datetime]] = {}

    def is_allowed(self, client_id: str, max_requests: int = RATE_LIMIT_MAX,
                   window_seconds: int = RATE_LIMIT_WINDOW) -> tuple[bool, dict]:
        """
        Check if client is within rate limit.
        Returns: (allowed: bool, metadata: dict)
        """
        now = datetime.utcnow()
        window_start = now - timedelta(seconds=window_seconds)

        # Clean old entries
        if client_id in self.requests:
            self.requests[client_id] = [
                ts for ts in self.requests[client_id]
                if ts > window_start
            ]
        else:
            self.requests[client_id] = []

        # Count requests in current window
        current_count = len(self.requests[client_id])

        # Check if under limit
        if current_count >= max_requests:
            # Calculate retry-after time
            oldest_request = min(self.requests[client_id]) if self.requests[client_id] else now
            retry_after = int((oldest_request + timedelta(seconds=window_seconds) - now).total_seconds())

            return False, {
                "current_count": current_count,
                "limit": max_requests,
                "window": window_seconds,
                "retry_after": max(retry_after, 1)
            }

        # Record this request
        self.requests[client_id].append(now)

        return True, {
            "current_count": current_count + 1,
            "limit": max_requests,
            "window": window_seconds,
            "remaining": max_requests - current_count - 1
        }

    def cleanup_old_entries(self):
        """Cleanup entries older than 2x window (periodic maintenance)."""
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=RATE_LIMIT_WINDOW * 2)

        for client_id in list(self.requests.keys()):
            self.requests[client_id] = [
                ts for ts in self.requests[client_id]
                if ts > cutoff
            ]
            # Remove empty entries
            if not self.requests[client_id]:
                del self.requests[client_id]


# Global rate limiter instance
rate_limiter = RateLimiter()


def verify_api_key(api_key: Optional[str]) -> Optional[str]:
    """
    Verify API key and return client identifier.
    Returns None if invalid.
    """
    if not api_key:
        return None

    # Hash provided key
    key_hash = hashlib.sha256(api_key.encode()).hexdigest()

    # Check against valid keys
    valid_keys = get_valid_api_keys()
    if key_hash in valid_keys:
        return valid_keys[key_hash]

    return None


async def auth_middleware(request: Request, call_next):
    """
    Authentication middleware.
    Requires API key for all endpoints except health check.
    """
    # Skip auth for health check and docs
    if request.url.path in ["/", "/health", "/docs", "/redoc", "/openapi.json"]:
        response = await call_next(request)
        return response

    # Check for API key
    api_key = request.headers.get("X-API-Key", "")

    # Development mode: Allow requests without API key
    if os.getenv("ENVIRONMENT") == "development":
        logger.debug(f"Development mode: Allowing request without API key to {request.url.path}")
        response = await call_next(request)
        return response

    # Production mode: Require API key
    client_id = verify_api_key(api_key)

    if not client_id:
        client_ip = request.client.host if request.client else "unknown"
        # Log security event
        security_logger.warning(
            f"Authentication failure: Invalid or missing API key",
            extra={
                "event_type": "auth_failure",
                "ip_address": client_ip,
                "endpoint": request.url.path,
                "method": request.method,
                "api_key_provided": bool(api_key),
            }
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
            headers={"WWW-Authenticate": "ApiKey"}
        )

    # Add client_id to request state for logging
    request.state.client_id = client_id

    response = await call_next(request)
    return response


async def rate_limit_middleware(request: Request, call_next):
    """
    Rate limiting middleware.
    Limits requests per client (by IP + API key).
    """
    # Skip rate limiting for health check
    if request.url.path in ["/", "/health", "/docs", "/redoc", "/openapi.json"]:
        response = await call_next(request)
        return response

    # Get client identifier (IP + API key hash)
    client_ip = request.client.host if request.client else "unknown"
    api_key = request.headers.get("X-API-Key", "")

    # Create unique client ID
    client_id = hashlib.sha256(f"{client_ip}:{api_key}".encode()).hexdigest()[:16]

    # Check rate limit
    allowed, metadata = rate_limiter.is_allowed(client_id)

    if not allowed:
        # Log security event
        security_logger.warning(
            f"Rate limit exceeded",
            extra={
                "event_type": "rate_limit_exceeded",
                "client_id": client_id,
                "ip_address": client_ip,
                "endpoint": request.url.path,
                "method": request.method,
                "current_count": metadata["current_count"],
                "limit": metadata["limit"],
                "retry_after": metadata["retry_after"],
            }
        )
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=f"Rate limit exceeded. Try again in {metadata['retry_after']} seconds.",
            headers={
                "X-RateLimit-Limit": str(metadata["limit"]),
                "X-RateLimit-Remaining": "0",
                "X-RateLimit-Reset": str(metadata["retry_after"]),
                "Retry-After": str(metadata["retry_after"])
            }
        )

    # Process request
    response = await call_next(request)

    # Add rate limit headers to response
    response.headers["X-RateLimit-Limit"] = str(metadata["limit"])
    response.headers["X-RateLimit-Remaining"] = str(metadata["remaining"])
    response.headers["X-RateLimit-Window"] = str(metadata["window"])

    return response


def get_rate_limit_stats() -> dict:
    """Get current rate limit statistics (for monitoring)."""
    return {
        "total_clients": len(rate_limiter.requests),
        "active_requests": sum(len(reqs) for reqs in rate_limiter.requests.values()),
        "limit_per_window": RATE_LIMIT_MAX,
        "window_seconds": RATE_LIMIT_WINDOW
    }
