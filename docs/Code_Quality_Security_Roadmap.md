# WebTics Code Quality & Security Roadmap

**Focus:** High-quality development practices and vulnerability minimization
**Goal:** Production-ready code suitable for medical/health research (without formal certification)
**Timeline:** 2-4 months for core improvements

---

## Executive Summary

WebTics handles sensitive health data for ADHD assessment and therapeutic games. While formal UK Class I certification is not required, **development standards should match medical device quality** to minimize vulnerabilities and ensure research integrity.

This roadmap focuses on **practical security improvements and development best practices** that can be implemented incrementally.

**Priority Areas:**
1. **Input Validation & Data Integrity** - Prevent data corruption
2. **Security Hardening** - Minimize attack surface
3. **Automated Testing** - Catch bugs before production
4. **Error Handling & Logging** - Detect and respond to issues
5. **Code Review & Documentation** - Maintainability and knowledge transfer

---

## High-Priority Security Improvements

### 1. Input Validation & Sanitization

**Risk:** Malicious or malformed data could corrupt database, cause crashes, or enable injection attacks.

**Current Gap:** Limited validation on event data, no range checks for numeric values.

#### Implementation: Data Validation Middleware

**File:** `backend/app/middleware/data_validation.py`

```python
"""
Comprehensive input validation for WebTics API.
Prevents data corruption, injection attacks, and invalid state.
"""

from fastapi import Request, HTTPException
from datetime import datetime, timezone
import re
import logging

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
    required = ["event_type", "timestamp"]
    for field in required:
        if field not in event_data:
            raise ValidationError(f"Missing required field: {field}")

    # Validate event types
    validate_numeric_range(event_data["event_type"], "event_type")
    if "event_subtype" in event_data:
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

    # Validate timestamp
    validate_timestamp(event_data["timestamp"])

    # Validate additional data JSON (if present)
    if "data" in event_data and event_data["data"]:
        if not isinstance(event_data["data"], dict):
            raise ValidationError("'data' field must be a JSON object")
        # Check JSON depth and size
        import json
        json_str = json.dumps(event_data["data"])
        if len(json_str) > 10000:  # 10KB limit
            raise ValidationError("'data' JSON exceeds 10KB limit")

async def validation_middleware(request: Request, call_next):
    """FastAPI middleware to validate all incoming requests."""

    # Validate event creation
    if request.method == "POST" and request.url.path.startswith("/api/v1/events"):
        try:
            body = await request.json()
            validate_event_data(body)
        except ValidationError as e:
            logger.warning(f"Validation failed: {e}")
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Unexpected validation error: {e}")
            raise HTTPException(status_code=400, detail="Invalid request data")

    # Validate session creation
    if request.method == "POST" and request.url.path.startswith("/api/v1/sessions"):
        try:
            body = await request.json()
            if "unique_id" in body:
                validate_string_safe(body["unique_id"], "unique_id", max_length=100)
            if "build_number" in body:
                validate_string_safe(body["build_number"], "build_number", max_length=50)
        except ValidationError as e:
            logger.warning(f"Validation failed: {e}")
            raise HTTPException(status_code=400, detail=str(e))

    response = await call_next(request)
    return response
```

**Integration:** Add to `backend/app/main.py`:

```python
from .middleware.data_validation import validation_middleware

app.middleware("http")(validation_middleware)
```

**Testing:**

```python
# backend/tests/test_validation.py
import pytest
from app.middleware.data_validation import validate_event_data, ValidationError

def test_valid_event():
    event = {
        "event_type": 102,
        "timestamp": "2026-02-16T12:00:00Z",
        "magnitude": 250.5,
    }
    validate_event_data(event)  # Should not raise

def test_reaction_time_too_high():
    event = {
        "event_type": 102,  # CORRECT_RESPONSE
        "timestamp": "2026-02-16T12:00:00Z",
        "magnitude": 15000,  # 15 seconds - unrealistic
    }
    with pytest.raises(ValidationError, match="outside valid range"):
        validate_event_data(event)

def test_future_timestamp():
    from datetime import datetime, timedelta
    future = (datetime.utcnow() + timedelta(hours=1)).isoformat() + "Z"
    event = {
        "event_type": 100,
        "timestamp": future,
    }
    with pytest.raises(ValidationError, match="in the future"):
        validate_event_data(event)

def test_missing_required_field():
    event = {"event_type": 100}  # Missing timestamp
    with pytest.raises(ValidationError, match="Missing required field"):
        validate_event_data(event)
```

**Estimated Effort:** 2-3 days development + 1-2 days testing

---

### 2. SQL Injection Prevention

**Risk:** Malicious SQL in user input could compromise database.

**Current Status:** ✅ **Good** - Using SQLAlchemy ORM with parameterized queries

**Verification Needed:** Ensure no raw SQL queries with string interpolation.

**Action:** Code audit for dangerous patterns:

```bash
# Search for potential SQL injection vulnerabilities
grep -r "execute(.*%.*)" backend/
grep -r "execute(.*f\".*)" backend/
grep -r "execute(.*+.*)" backend/
```

**Safe Pattern (SQLAlchemy ORM):**
```python
# GOOD: Parameterized query
session.query(Event).filter(Event.event_type == user_input).all()

# GOOD: Explicit parameters
session.execute(text("SELECT * FROM events WHERE event_type = :type"), {"type": user_input})
```

**Dangerous Pattern (avoid):**
```python
# BAD: String formatting
session.execute(f"SELECT * FROM events WHERE event_type = {user_input}")

# BAD: String concatenation
session.execute("SELECT * FROM events WHERE event_type = " + user_input)
```

**Estimated Effort:** 1 day code audit

---

### 3. Authentication & Authorization Hardening

**Risk:** Unauthorized access to sensitive health data.

**Current Gap:** Basic or no authentication on API endpoints.

#### Implementation: API Key Authentication + Rate Limiting

**File:** `backend/app/middleware/auth.py`

```python
"""
API authentication and rate limiting.
Prevents unauthorized access and abuse.
"""

from fastapi import HTTPException, Security, Request
from fastapi.security import APIKeyHeader
from datetime import datetime, timedelta
import hashlib
import os

API_KEY_HEADER = APIKeyHeader(name="X-API-Key", auto_error=False)

# In production: Store in database with proper hashing
# For now: Environment variable (hash it for comparison)
VALID_API_KEYS = {
    hashlib.sha256(os.getenv("WEBTICS_API_KEY", "").encode()).hexdigest(): "default_client"
}

# Rate limiting: Simple in-memory store (use Redis in production)
REQUEST_COUNTS = {}
RATE_LIMIT_WINDOW = 60  # seconds
RATE_LIMIT_MAX = 100  # requests per window

def verify_api_key(api_key: str = Security(API_KEY_HEADER)) -> str:
    """Verify API key and return client identifier."""
    if not api_key:
        raise HTTPException(status_code=401, detail="Missing API key")

    key_hash = hashlib.sha256(api_key.encode()).hexdigest()
    if key_hash not in VALID_API_KEYS:
        raise HTTPException(status_code=401, detail="Invalid API key")

    return VALID_API_KEYS[key_hash]

async def rate_limit_middleware(request: Request, call_next):
    """Rate limiting to prevent abuse."""
    # Get client identifier (IP + API key if present)
    client_ip = request.client.host
    api_key = request.headers.get("X-API-Key", "")
    client_id = hashlib.sha256(f"{client_ip}:{api_key}".encode()).hexdigest()

    now = datetime.utcnow()
    window_start = now - timedelta(seconds=RATE_LIMIT_WINDOW)

    # Clean old entries
    REQUEST_COUNTS[client_id] = [
        ts for ts in REQUEST_COUNTS.get(client_id, [])
        if ts > window_start
    ]

    # Check rate limit
    if len(REQUEST_COUNTS.get(client_id, [])) >= RATE_LIMIT_MAX:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    # Record request
    REQUEST_COUNTS.setdefault(client_id, []).append(now)

    response = await call_next(request)
    return response
```

**Environment Variable Setup:**

```bash
# Generate strong API key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Set in .env
WEBTICS_API_KEY=<generated_key>
```

**Godot SDK Update:**

```gdscript
# sdk/godot/addons/webtics/WebTics.gd
var api_key: String = ""

func configure(url: String, p_api_key: String = "") -> void:
    base_url = url
    api_key = p_api_key

func _make_request(endpoint: String, method: int, data: Dictionary) -> void:
    var http = HTTPRequest.new()
    add_child(http)

    var headers = ["Content-Type: application/json"]
    if api_key != "":
        headers.append("X-API-Key: " + api_key)

    # ... rest of request
```

**Estimated Effort:** 2-3 days development + testing

---

### 4. Secrets Management

**Risk:** Hardcoded secrets (database passwords, API keys) in code or version control.

**Current Gap:** Secrets in `docker-compose.yml` (development only, but still risky).

#### Implementation: Environment Variables + `.env` File

**File:** `.env.example` (commit to git)

```bash
# WebTics Configuration
# Copy to .env and fill in production values

# Database
POSTGRES_USER=webtics
POSTGRES_PASSWORD=CHANGE_ME_IN_PRODUCTION
POSTGRES_DB=webtics
DATABASE_URL=postgresql://webtics:CHANGE_ME@db:5432/webtics

# API Security
WEBTICS_API_KEY=GENERATE_WITH_secrets.token_urlsafe_32
SECRET_KEY=GENERATE_WITH_secrets.token_urlsafe_64

# CORS (comma-separated origins)
ALLOWED_ORIGINS=http://localhost:3000,https://yourdomain.com

# Optional: Sentry error tracking
SENTRY_DSN=
```

**File:** `.env` (add to `.gitignore`, never commit)

```bash
# Actual production secrets (DO NOT COMMIT)
POSTGRES_PASSWORD=<strong_random_password>
WEBTICS_API_KEY=<generated_api_key>
SECRET_KEY=<generated_secret_key>
```

**Update:** `docker-compose.yml`

```yaml
services:
  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    env_file:
      - .env

  backend:
    build: ./backend
    environment:
      DATABASE_URL: ${DATABASE_URL}
      SECRET_KEY: ${SECRET_KEY}
      ALLOWED_ORIGINS: ${ALLOWED_ORIGINS}
    env_file:
      - .env
```

**Update:** `.gitignore`

```
.env
*.env
.env.local
.env.production
```

**Secrets Generation Script:**

```bash
#!/bin/bash
# scripts/generate_secrets.sh

echo "Generating secure secrets for WebTics..."

POSTGRES_PASSWORD=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
API_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(64))")

cat > .env <<EOF
# WebTics Production Secrets
# Generated: $(date)

POSTGRES_USER=webtics
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
POSTGRES_DB=webtics
DATABASE_URL=postgresql://webtics:${POSTGRES_PASSWORD}@db:5432/webtics

WEBTICS_API_KEY=${API_KEY}
SECRET_KEY=${SECRET_KEY}

ALLOWED_ORIGINS=http://localhost:3000
EOF

echo "✅ Secrets generated and saved to .env"
echo "⚠️  Keep .env secure and never commit to git!"
```

**Estimated Effort:** 1 day

---

### 5. HTTPS/TLS Enforcement

**Risk:** Data transmitted in plaintext could be intercepted (man-in-the-middle attacks).

**Current Gap:** Development uses HTTP, production should enforce HTTPS.

#### Implementation: HTTPS Redirect + HSTS Header

**File:** `backend/app/middleware/security.py`

```python
"""
Security middleware: HTTPS enforcement, security headers.
"""

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Add security headers to all responses."""

    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)

        # HSTS: Force HTTPS for 1 year
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"

        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # XSS protection
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Referrer policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Content Security Policy (adjust for your needs)
        response.headers["Content-Security-Policy"] = "default-src 'self'; script-src 'self'"

        return response

async def https_redirect_middleware(request: Request, call_next):
    """Redirect HTTP to HTTPS in production."""
    import os

    if os.getenv("ENVIRONMENT") == "production":
        if request.url.scheme != "https":
            # Redirect to HTTPS
            https_url = request.url.replace(scheme="https")
            return RedirectResponse(url=str(https_url), status_code=301)

    response = await call_next(request)
    return response
```

**Integration:**

```python
from .middleware.security import SecurityHeadersMiddleware, https_redirect_middleware

app.add_middleware(SecurityHeadersMiddleware)
app.middleware("http")(https_redirect_middleware)
```

**Nginx Configuration (Production):**

```nginx
# nginx/webtics.conf
server {
    listen 80;
    server_name webtics.yourdomain.com;

    # Redirect all HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name webtics.yourdomain.com;

    # SSL/TLS Configuration
    ssl_certificate /etc/ssl/certs/webtics.crt;
    ssl_certificate_key /etc/ssl/private/webtics.key;
    ssl_protocols TLSv1.3 TLSv1.2;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256';
    ssl_prefer_server_ciphers on;

    # HSTS
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;

    location / {
        proxy_pass http://localhost:8013;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

**Estimated Effort:** 1-2 days + SSL certificate setup

---

## Medium-Priority Code Quality Improvements

### 6. Automated Testing Suite

**Goal:** Catch regressions, ensure code quality, enable confident refactoring.

**Current Gap:** Limited test coverage.

#### Test Structure

```
backend/tests/
├── test_validation.py      # Input validation tests
├── test_auth.py            # Authentication tests
├── test_events.py          # Event API tests
├── test_sessions.py        # Session API tests
├── test_research.py        # Consent/withdrawal tests
├── test_security.py        # Security tests (injection, XSS, etc.)
└── test_integration.py     # End-to-end tests
```

#### Critical Test Cases

**File:** `backend/tests/test_security.py`

```python
"""
Security-focused tests to prevent vulnerabilities.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_sql_injection_attempt():
    """Attempt SQL injection in event_type field."""
    malicious_payload = {
        "event_type": "1; DROP TABLE events; --",
        "timestamp": "2026-02-16T12:00:00Z",
    }
    response = client.post("/api/v1/events", json=malicious_payload)

    # Should reject (400 Bad Request or validation error)
    assert response.status_code in [400, 422]

    # Verify events table still exists
    response = client.get("/api/v1/events")
    assert response.status_code in [200, 401]  # Table exists (200 or needs auth)

def test_xss_in_json_data():
    """Attempt XSS injection in JSON data field."""
    malicious_payload = {
        "event_type": 100,
        "timestamp": "2026-02-16T12:00:00Z",
        "data": {
            "comment": "<script>alert('XSS')</script>"
        }
    }
    response = client.post("/api/v1/events", json=malicious_payload)

    # Should store safely (FastAPI escapes JSON)
    # Verify no script execution on retrieval
    if response.status_code == 201:
        event_id = response.json()["id"]
        get_response = client.get(f"/api/v1/events/{event_id}")
        assert "<script>" not in get_response.text  # Should be escaped

def test_path_traversal_attempt():
    """Attempt directory traversal in file-related endpoints."""
    malicious_paths = [
        "../../../etc/passwd",
        "..\\..\\..\\windows\\system32\\config\\sam",
        "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
    ]

    for path in malicious_paths:
        # Example: if there's an export endpoint
        response = client.get(f"/api/v1/export/{path}")
        assert response.status_code in [400, 404, 422]  # Rejected

def test_excessive_request_size():
    """Reject overly large payloads (DoS prevention)."""
    huge_data = {"data": {"x": "A" * 1000000}}  # 1MB of 'A's
    response = client.post("/api/v1/events", json=huge_data)

    # Should reject (413 Payload Too Large or 400)
    assert response.status_code in [400, 413, 422]

def test_rate_limiting():
    """Verify rate limiting prevents abuse."""
    # Send 150 requests rapidly (exceeds 100/min limit)
    for i in range(150):
        response = client.get("/api/v1/health")
        if i >= 100:
            assert response.status_code == 429  # Rate limit exceeded

def test_unauthorized_access():
    """Verify endpoints require authentication."""
    # Without API key
    response = client.get("/api/v1/events")
    assert response.status_code == 401

    # With invalid API key
    headers = {"X-API-Key": "invalid_key_12345"}
    response = client.get("/api/v1/events", headers=headers)
    assert response.status_code == 401
```

**Run Tests:**

```bash
# Install pytest
pip install pytest pytest-cov

# Run all tests with coverage
pytest backend/tests/ --cov=backend/app --cov-report=html

# View coverage report
open htmlcov/index.html
```

**CI/CD Integration (GitHub Actions):**

**File:** `.github/workflows/tests.yml`

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_USER: webtics
          POSTGRES_PASSWORD: testpass
          POSTGRES_DB: webtics_test
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          pip install pytest pytest-cov

      - name: Run tests
        env:
          DATABASE_URL: postgresql://webtics:testpass@localhost:5432/webtics_test
        run: |
          cd backend
          pytest tests/ --cov=app --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v3
        with:
          files: ./backend/coverage.xml
```

**Estimated Effort:** 1-2 weeks for comprehensive test suite

---

### 7. Error Handling & Logging

**Goal:** Detect issues early, facilitate debugging, monitor production health.

#### Structured Logging

**File:** `backend/app/logging_config.py`

```python
"""
Structured logging configuration for WebTics.
Uses JSON format for easy parsing and analysis.
"""

import logging
import sys
from datetime import datetime

class JSONFormatter(logging.Formatter):
    """Format log records as JSON for structured logging."""

    def format(self, record):
        import json

        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add custom fields
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id

        return json.dumps(log_data)

def setup_logging(level=logging.INFO):
    """Configure application logging."""

    # Root logger
    logger = logging.getLogger()
    logger.setLevel(level)

    # Console handler (JSON format)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(JSONFormatter())
    logger.addHandler(console_handler)

    # File handler (rotate daily)
    from logging.handlers import TimedRotatingFileHandler
    file_handler = TimedRotatingFileHandler(
        "/var/log/webtics/app.log",
        when="midnight",
        interval=1,
        backupCount=30  # Keep 30 days
    )
    file_handler.setFormatter(JSONFormatter())
    logger.addHandler(file_handler)

    # Error file handler (errors only)
    error_handler = TimedRotatingFileHandler(
        "/var/log/webtics/error.log",
        when="midnight",
        interval=1,
        backupCount=90  # Keep 90 days for errors
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(JSONFormatter())
    logger.addHandler(error_handler)

    return logger
```

**Usage in Application:**

```python
# backend/app/main.py
from .logging_config import setup_logging

logger = setup_logging()

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch all unhandled exceptions and log them."""
    logger.error(
        f"Unhandled exception: {exc}",
        exc_info=True,
        extra={
            "request_path": request.url.path,
            "request_method": request.method,
            "client_ip": request.client.host,
        }
    )

    # Don't expose internal errors to clients
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please contact support."}
    )
```

**Estimated Effort:** 2-3 days

---

### 8. Dependency Security Scanning

**Goal:** Detect known vulnerabilities in third-party dependencies.

#### Tools

**Safety:** Python dependency vulnerability scanner

```bash
# Install
pip install safety

# Scan dependencies
safety check --file requirements.txt

# Output example:
# +==============================================================================+
# |                                                                              |
# |                               /$$$$$$            /$$                         |
# |                              /$$__  $$          | $$                         |
# |           /$$$$$$$  /$$$$$$ | $$  \__//$$$$$$  /$$$$$$   /$$   /$$           |
# |          /$$_____/ |____  $$| $$$$   /$$__  $$|_  $$_/  | $$  | $$           |
# |         |  $$$$$$   /$$$$$$$| $$_/  | $$$$$$$$  | $$    | $$  | $$           |
# |          \____  $$ /$$__  $$| $$    | $$_____/  | $$ /$$| $$  | $$           |
# |          /$$$$$$$/|  $$$$$$$| $$    |  $$$$$$$  |  $$$$/|  $$$$$$$           |
# |         |_______/  \_______/|__/     \_______/   \___/   \____  $$           |
# |                                                          /$$  | $$           |
# |                                                         |  $$$$$$/           |
# |  by pyup.io                                              \______/            |
# |                                                                              |
# +==============================================================================+
```

**Dependabot (GitHub):** Automatically creates PRs for dependency updates

**File:** `.github/dependabot.yml`

```yaml
version: 2
updates:
  - package-ecosystem: "pip"
    directory: "/backend"
    schedule:
      interval: "weekly"
    open-pull-requests-limit: 10

  - package-ecosystem: "docker"
    directory: "/"
    schedule:
      interval: "weekly"
```

**Trivy:** Container vulnerability scanner

```bash
# Install
brew install trivy  # macOS
# or
apt-get install trivy  # Ubuntu

# Scan Docker image
docker build -t webtics_backend ./backend
trivy image webtics_backend

# Scan file system
trivy fs ./backend
```

**Automated CI Check:**

**File:** `.github/workflows/security.yml`

```yaml
name: Security Scan

on: [push, pull_request]

jobs:
  dependency-scan:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Run Safety check
        run: |
          pip install safety
          safety check --file backend/requirements.txt --json

      - name: Run Trivy scan
        uses: aquasecurity/trivy-action@master
        with:
          scan-type: 'fs'
          scan-ref: './backend'
          severity: 'CRITICAL,HIGH'
```

**Estimated Effort:** 1 day setup, ongoing automated

---

### 9. Code Quality & Linting

**Goal:** Consistent code style, catch common bugs, improve maintainability.

#### Tools

**Black:** Python code formatter

```bash
# Install
pip install black

# Format all code
black backend/app/

# Check without modifying
black --check backend/app/
```

**Ruff:** Fast Python linter (replaces flake8, isort, etc.)

```bash
# Install
pip install ruff

# Lint code
ruff check backend/app/

# Auto-fix issues
ruff check --fix backend/app/
```

**MyPy:** Type checking

```bash
# Install
pip install mypy

# Check types
mypy backend/app/
```

**Pre-commit Hooks:** Run checks before commit

**File:** `.pre-commit-config.yaml`

```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 24.1.0
    hooks:
      - id: black
        language_version: python3.11

  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.15
    hooks:
      - id: ruff
        args: [--fix]

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
      - id: check-merge-conflict
```

**Setup:**

```bash
pip install pre-commit
pre-commit install  # Install git hooks
pre-commit run --all-files  # Test on all files
```

**Estimated Effort:** 1 day setup

---

## Implementation Timeline

### Sprint 1: Security Foundations (Week 1-2)

- [ ] Input validation middleware
- [ ] Secrets management (.env files)
- [ ] SQL injection audit
- [ ] Security headers

**Deliverables:** Validated inputs, no hardcoded secrets, basic security headers

---

### Sprint 2: Authentication & Testing (Week 3-4)

- [ ] API key authentication
- [ ] Rate limiting
- [ ] Security test suite
- [ ] CI/CD pipeline (GitHub Actions)

**Deliverables:** Protected API, automated tests, CI pipeline

---

### Sprint 3: Logging & Monitoring (Week 5-6)

- [ ] Structured logging (JSON format)
- [ ] Error handling improvements
- [ ] Log rotation setup
- [ ] Basic monitoring dashboard

**Deliverables:** Production-ready logging, error tracking

---

### Sprint 4: Code Quality (Week 7-8)

- [ ] Dependency scanning (Safety, Trivy)
- [ ] Code formatting (Black)
- [ ] Linting (Ruff)
- [ ] Pre-commit hooks
- [ ] Type checking (MyPy)

**Deliverables:** Clean codebase, automated quality checks

---

### Sprint 5: HTTPS & Deployment (Week 9-10)

- [ ] HTTPS enforcement
- [ ] SSL certificate setup
- [ ] Nginx configuration
- [ ] Production deployment guide

**Deliverables:** Secure production deployment

---

## Success Metrics

**Security:**
- ✅ 0 high/critical vulnerabilities in dependency scan
- ✅ 100% API endpoints require authentication
- ✅ All inputs validated
- ✅ HTTPS enforced in production

**Code Quality:**
- ✅ >80% test coverage
- ✅ 0 linting errors
- ✅ Type hints on all public functions
- ✅ CI pipeline passing

**Reliability:**
- ✅ <1% error rate in production
- ✅ All errors logged and monitored
- ✅ Automated backups tested weekly

---

## Maintenance Plan

**Daily:**
- Monitor error logs for anomalies
- Check CI/CD pipeline status

**Weekly:**
- Review dependency scan results
- Test database backup restore
- Review rate limit logs (detect abuse)

**Monthly:**
- Update dependencies (security patches)
- Review test coverage metrics
- Audit access logs

**Quarterly:**
- External security audit (penetration testing)
- Review and update security policies
- Disaster recovery drill

---

## Resources & Tools

**Development:**
- [FastAPI Security Best Practices](https://fastapi.tiangolo.com/tutorial/security/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [SQLAlchemy Security](https://docs.sqlalchemy.org/en/20/faq/security.html)

**Testing:**
- [pytest documentation](https://docs.pytest.org/)
- [pytest-cov coverage plugin](https://pytest-cov.readthedocs.io/)

**Security Tools:**
- [Safety vulnerability scanner](https://github.com/pyupio/safety)
- [Trivy container scanner](https://github.com/aquasecurity/trivy)
- [Bandit security linter](https://github.com/PyCQA/bandit)

**Code Quality:**
- [Black code formatter](https://black.readthedocs.io/)
- [Ruff linter](https://docs.astral.sh/ruff/)
- [MyPy type checker](https://mypy-lang.org/)

---

## Conclusion

This roadmap prioritizes **practical security improvements** over regulatory compliance documentation. By implementing these changes incrementally over 2-4 months, WebTics will achieve:

1. **Strong security posture** suitable for health data
2. **High code quality** enabling confident development
3. **Automated testing** catching bugs before production
4. **Monitoring & logging** for operational visibility
5. **Maintainable codebase** for long-term sustainability

All improvements are **actionable and testable**, with clear success criteria and timelines.

**Next Steps:**
1. Review and prioritize sprint items based on current needs
2. Set up development environment with security tools
3. Begin Sprint 1: Security Foundations

---

**Document Version:** 1.0
**Last Updated:** February 16, 2026
**Status:** Active Roadmap
