"""
Data validation middleware for WebTics.
Implements input validation, range checks, and error logging.
Prevents data corruption and injection attacks.
"""

from fastapi import Request
from fastapi.responses import JSONResponse
from datetime import datetime, timezone
import re
import logging
import json

logger = logging.getLogger("webtics.validation")

# Validation rules based on domain knowledge
VALIDATION_RULES = {
    "reaction_time_ms": {"min": 0, "max": 10000, "description": "Human reaction time 0-10 seconds"},
    "accuracy_percent": {"min": 0, "max": 100, "description": "Percentage 0-100"},
    "session_duration_sec": {"min": 0, "max": 86400, "description": "Max 24 hours"},
    "coordinates": {"min": -10000, "max": 10000, "description": "Game coordinates"},
    "event_type": {"min": 0, "max": 999, "description": "Event type enum"},
    "event_subtype": {"min": 0, "max": 999, "description": "Event subtype enum"},
}

# String validation patterns
SAFE_STRING_PATTERN = re.compile(r'^[a-zA-Z0-9_\-\.]+$')
UUID_PATTERN = re.compile(r'^[a-f0-9]{8}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{4}-[a-f0-9]{12}$', re.I)


class ValidationError(Exception):
    """Custom exception for validation failures."""
    pass


def validate_numeric_range(value: float, field_name: str) -> None:
    """Validate numeric value is within acceptable range."""
    if field_name not in VALIDATION_RULES:
        return  # No rule defined, skip validation

    rule = VALIDATION_RULES[field_name]
    if not (rule["min"] <= value <= rule["max"]):
        raise ValidationError(
            f"{field_name} value {value} outside valid range "
            f"[{rule['min']}, {rule['max']}]. {rule['description']}"
        )


def validate_string_safe(value: str, field_name: str, max_length: int = 255) -> None:
    """Validate string is safe (alphanumeric + basic punctuation only)."""
    if len(value) > max_length:
        raise ValidationError(f"{field_name} exceeds max length {max_length}")

    if not SAFE_STRING_PATTERN.match(value):
        raise ValidationError(
            f"{field_name} contains invalid characters. "
            f"Only alphanumeric, underscore, hyphen, dot allowed."
        )


def validate_timestamp(timestamp_str: str) -> datetime:
    """Validate timestamp is valid ISO 8601 format and not in future."""
    try:
        dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
    except ValueError as e:
        raise ValidationError(f"Invalid timestamp format: {e}")

    # Check timestamp is not in future (allow 5 min clock skew)
    now = datetime.now(timezone.utc)
    max_future = now.timestamp() + 300  # 5 minutes

    if dt.timestamp() > max_future:
        raise ValidationError(
            f"Timestamp {timestamp_str} is in the future (server time: {now.isoformat()})"
        )

    return dt


def validate_event_data(event_data: dict) -> None:
    """Validate event data structure and values."""

    # Required fields
    required = ["event_type"]
    for field in required:
        if field not in event_data:
            raise ValidationError(f"Missing required field: {field}")

    # Validate event types
    validate_numeric_range(event_data["event_type"], "event_type")
    if "event_subtype" in event_data and event_data["event_subtype"] is not None:
        validate_numeric_range(event_data["event_subtype"], "event_subtype")

    # Validate coordinates
    for coord in ["x", "y", "z"]:
        if coord in event_data and event_data[coord] is not None:
            validate_numeric_range(event_data[coord], "coordinates")

    # Validate magnitude (used for reaction times, scores, etc.)
    if "magnitude" in event_data and event_data["magnitude"] is not None:
        mag = event_data["magnitude"]
        # Infer validation rule based on event type
        event_type = event_data["event_type"]
        if event_type in [102, 103]:  # CORRECT_RESPONSE, INCORRECT_RESPONSE
            validate_numeric_range(mag, "reaction_time_ms")
        elif event_type in [104, 105]:  # TASK_SCORE
            validate_numeric_range(mag, "accuracy_percent")

    # Validate timestamp if present
    if "timestamp" in event_data and event_data["timestamp"]:
        validate_timestamp(event_data["timestamp"])

    # Validate additional data JSON (if present)
    if "data" in event_data and event_data["data"]:
        if not isinstance(event_data["data"], dict):
            raise ValidationError("'data' field must be a JSON object")
        # Check JSON size
        json_str = json.dumps(event_data["data"])
        if len(json_str) > 10000:  # 10KB limit
            raise ValidationError("'data' JSON exceeds 10KB limit")


def validate_session_data(session_data: dict) -> None:
    """Validate session creation data."""
    if "unique_id" in session_data and session_data["unique_id"]:
        validate_string_safe(session_data["unique_id"], "unique_id", max_length=100)

    if "build_number" in session_data and session_data["build_number"]:
        # Build number can have dots for versioning like "1.0.2"
        if len(session_data["build_number"]) > 50:
            raise ValidationError("build_number exceeds max length 50")


def _validate_body(body: dict, path: str) -> None:
    """Dispatch validation by path. Raises ValidationError on failure."""
    if path.startswith("/api/v1/events"):
        validate_event_data(body)
    elif path.startswith("/api/v1/sessions"):
        validate_session_data(body)


async def validation_middleware(request: Request, call_next):
    """Validate incoming event/session POSTs.

    NOTE: exceptions raised inside Starlette HTTP middleware are NOT turned into
    responses by FastAPI's exception handlers (they propagate to the server error
    handler and surface as 500). So we must *return* a JSONResponse here, not raise.
    """
    path = request.url.path
    if request.method == "POST" and (
        path.startswith("/api/v1/events") or path.startswith("/api/v1/sessions")
    ):
        try:
            body = await request.json()
            _validate_body(body, path)
        except ValidationError as e:
            logger.warning(f"Validation failed for {path}: {e}")
            return JSONResponse(status_code=400, content={"detail": str(e)})
        except json.JSONDecodeError as e:
            logger.warning(f"Invalid JSON for {path}: {e}")
            return JSONResponse(status_code=400, content={"detail": "Invalid JSON format"})
        except Exception as e:
            logger.error(f"Unexpected validation error for {path}: {e}", exc_info=True)
            return JSONResponse(status_code=400, content={"detail": "Invalid request data"})

    return await call_next(request)
