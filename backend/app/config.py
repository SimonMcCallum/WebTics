"""Centralised configuration for the teaching service.

All values come from environment variables with safe development defaults.
Production values are injected via the home-server ``.env`` (see Deployment_Guide.md).
"""
import os


def _int(name: str, default: int) -> int:
    try:
        return int(os.getenv(name, str(default)))
    except (TypeError, ValueError):
        return default


# --- Auth -------------------------------------------------------------------
JWT_SECRET = os.getenv("JWT_SECRET", os.getenv("SECRET_KEY", "dev_jwt_secret_change_me"))
JWT_ALGORITHM = "HS256"
# Short-lived access tokens; time-limited accounts are additionally checked per request.
ACCESS_TOKEN_EXPIRE_MINUTES = _int("ACCESS_TOKEN_EXPIRE_MINUTES", 720)  # 12h

# --- Ingest -----------------------------------------------------------------
# When True the legacy open endpoints accept events without game credentials.
# MUST be False in production (set in .env).
ALLOW_ANON_INGEST = os.getenv("ALLOW_ANON_INGEST", "true").lower() in ("1", "true", "yes")

# Public base URL used in snippets / docs shown to students.
PUBLIC_BASE_URL = os.getenv("PUBLIC_BASE_URL", "http://localhost:8013")

# --- Default per-game quotas (Modest tier; admin-overridable per game) -------
DEFAULT_RATE_PER_MIN = _int("WEBTICS_DEFAULT_RATE_PER_MIN", 60)
DEFAULT_BURST = _int("WEBTICS_DEFAULT_BURST", 600)
DEFAULT_MAX_BYTES = _int("WEBTICS_DEFAULT_MAX_BYTES", 100 * 1024 * 1024)  # 100 MB
# Aggregate cap across all of a student's games.
DEFAULT_USER_MAX_BYTES = _int("WEBTICS_DEFAULT_USER_MAX_BYTES", 250 * 1024 * 1024)  # 250 MB

# Estimated fixed per-event storage overhead (row + indexes), added to payload size.
EVENT_ROW_OVERHEAD_BYTES = _int("WEBTICS_EVENT_ROW_OVERHEAD_BYTES", 200)

# --- Branding ---------------------------------------------------------------
# Student-facing brand vs professional service brand (same backend).
STUDENT_BRAND = os.getenv("WEBTICS_STUDENT_BRAND", "Ludogogy Logging")
SERVICE_BRAND = os.getenv("WEBTICS_SERVICE_BRAND", "WebTics")
