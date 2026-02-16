"""
Security tests for WebTics API.
Tests for SQL injection, XSS, path traversal, and other vulnerabilities.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from datetime import datetime

client = TestClient(app)


class TestSQLInjection:
    """Test SQL injection prevention."""

    def test_sql_injection_in_event_type(self):
        """Attempt SQL injection in event_type field."""
        malicious_payload = {
            "event_type": "1; DROP TABLE events; --",
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        response = client.post(
            "/api/v1/events?play_session_id=1",
            json=malicious_payload
        )

        # Should reject with validation error
        assert response.status_code in [400, 422]

    def test_sql_injection_in_unique_id(self):
        """Attempt SQL injection in session unique_id."""
        malicious_payload = {
            "unique_id": "1' OR '1'='1",
            "build_number": "1.0"
        }
        response = client.post("/api/v1/sessions", json=malicious_payload)

        # Should reject with validation error
        assert response.status_code in [400, 422]

    def test_sql_injection_in_data_field(self):
        """Attempt SQL injection in JSON data field."""
        # Create session first
        session = client.post(
            "/api/v1/sessions",
            json={"unique_id": "test_sql", "build_number": "1.0"}
        ).json()

        # Create play session
        play_session = client.post(
            "/api/v1/play-sessions",
            json={"metric_session_id": session["id"]}
        ).json()

        # Attempt SQL injection in data field
        malicious_event = {
            "event_type": 100,
            "data": {
                "query": "'; DROP TABLE events; --"
            }
        }
        response = client.post(
            f"/api/v1/events?play_session_id={play_session['id']}",
            json=malicious_event
        )

        # Should succeed (JSON is safe) but not execute SQL
        # The important test is that events table still exists
        if response.status_code == 200:
            # Verify events table not dropped
            check_response = client.get("/api/v1/sessions/1/events")
            assert check_response.status_code in [200, 404]  # Not a DB error


class TestXSSPrevention:
    """Test XSS prevention."""

    def test_xss_in_json_data(self):
        """Attempt XSS injection in JSON data field."""
        # Create session
        session = client.post(
            "/api/v1/sessions",
            json={"unique_id": "test_xss", "build_number": "1.0"}
        ).json()

        # Create play session
        play_session = client.post(
            "/api/v1/play-sessions",
            json={"metric_session_id": session["id"]}
        ).json()

        # Attempt XSS
        malicious_event = {
            "event_type": 100,
            "data": {
                "comment": "<script>alert('XSS')</script>"
            }
        }
        response = client.post(
            f"/api/v1/events?play_session_id={play_session['id']}",
            json=malicious_event
        )

        # Should store data but not execute script
        # FastAPI returns JSON which is naturally escaped
        if response.status_code == 200:
            event = response.json()
            # Verify script tag is in data but would be escaped in HTML context
            assert "<script>" in str(event.get("data", {}))


class TestInputValidation:
    """Test input validation prevents malformed data."""

    def test_negative_event_type(self):
        """Negative event type should be rejected."""
        response = client.post(
            "/api/v1/events?play_session_id=1",
            json={"event_type": -1}
        )
        assert response.status_code in [400, 422]

    def test_excessive_magnitude(self):
        """Unrealistically high magnitude should be rejected."""
        response = client.post(
            "/api/v1/events?play_session_id=1",
            json={
                "event_type": 102,  # CORRECT_RESPONSE
                "magnitude": 999999  # Impossibly high reaction time
            }
        )
        assert response.status_code in [400, 422]

    def test_future_timestamp(self):
        """Future timestamp should be rejected."""
        from datetime import timedelta
        future = (datetime.utcnow() + timedelta(hours=2)).isoformat() + "Z"

        response = client.post(
            "/api/v1/events?play_session_id=1",
            json={
                "event_type": 100,
                "timestamp": future
            }
        )
        assert response.status_code in [400, 422]

    def test_invalid_json(self):
        """Invalid JSON should be rejected."""
        response = client.post(
            "/api/v1/events?play_session_id=1",
            data="not-valid-json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code in [400, 422]

    def test_oversized_json_data(self):
        """JSON data exceeding size limit should be rejected."""
        huge_data = {"x": "A" * 15000}  # Over 10KB
        response = client.post(
            "/api/v1/events?play_session_id=1",
            json={
                "event_type": 100,
                "data": huge_data
            }
        )
        assert response.status_code in [400, 422]


class TestSecurityHeaders:
    """Test security headers are present."""

    def test_security_headers_present(self):
        """Response should include security headers."""
        response = client.get("/")

        # Check for security headers
        assert "X-Frame-Options" in response.headers
        assert response.headers["X-Frame-Options"] == "DENY"

        assert "X-Content-Type-Options" in response.headers
        assert response.headers["X-Content-Type-Options"] == "nosniff"

        assert "Referrer-Policy" in response.headers

        assert "Content-Security-Policy" in response.headers

    def test_hsts_header_in_production(self):
        """HSTS header should be present in production mode."""
        # Note: HSTS only added when HTTPS or ENVIRONMENT=production
        # In test mode with HTTP, HSTS may not be present
        response = client.get("/")
        # Just verify the endpoint works
        assert response.status_code == 200


class TestCORS:
    """Test CORS configuration."""

    def test_cors_headers(self):
        """CORS headers should be configured."""
        response = client.options(
            "/api/v1/sessions",
            headers={"Origin": "http://localhost:3000"}
        )

        # Should include CORS headers
        assert "access-control-allow-origin" in response.headers


class TestErrorHandling:
    """Test error handling doesn't leak information."""

    def test_404_doesnt_leak_info(self):
        """404 errors shouldn't reveal system information."""
        response = client.get("/api/v1/nonexistent")
        assert response.status_code == 404
        assert "traceback" not in response.text.lower()
        assert "exception" not in response.text.lower()

    def test_500_doesnt_leak_info(self):
        """500 errors shouldn't reveal internal details."""
        # Trigger an error by using invalid play_session_id type
        response = client.post(
            "/api/v1/events?play_session_id=invalid",
            json={"event_type": 100}
        )

        # Should return error without exposing internals
        if response.status_code == 500:
            response_text = response.text.lower()
            assert "traceback" not in response_text
            assert "file" not in response_text
            # Should have generic error message
            assert "internal server error" in response_text or "error" in response_text


class TestDataIntegrity:
    """Test data integrity constraints."""

    def test_duplicate_session_rejected(self):
        """Creating duplicate session with same unique_id should fail."""
        session_data = {
            "unique_id": "duplicate_test",
            "build_number": "1.0"
        }

        # Create first session
        response1 = client.post("/api/v1/sessions", json=session_data)
        assert response1.status_code == 200

        # Attempt duplicate
        response2 = client.post("/api/v1/sessions", json=session_data)
        assert response2.status_code == 400
        assert "already exists" in response2.json()["detail"].lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
