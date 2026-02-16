"""
Tests for data validation middleware.
Ensures input validation prevents data corruption and attacks.
"""

import pytest
from datetime import datetime, timedelta
from app.middleware.data_validation import (
    validate_event_data,
    validate_session_data,
    validate_numeric_range,
    validate_string_safe,
    validate_timestamp,
    ValidationError
)


class TestNumericValidation:
    """Test numeric range validation."""

    def test_valid_reaction_time(self):
        """Valid reaction time should pass."""
        validate_numeric_range(250.5, "reaction_time_ms")

    def test_reaction_time_too_high(self):
        """Reaction time over 10 seconds should fail."""
        with pytest.raises(ValidationError, match="outside valid range"):
            validate_numeric_range(15000, "reaction_time_ms")

    def test_reaction_time_negative(self):
        """Negative reaction time should fail."""
        with pytest.raises(ValidationError, match="outside valid range"):
            validate_numeric_range(-100, "reaction_time_ms")

    def test_valid_accuracy(self):
        """Valid accuracy percentage should pass."""
        validate_numeric_range(85.5, "accuracy_percent")

    def test_accuracy_over_100(self):
        """Accuracy over 100% should fail."""
        with pytest.raises(ValidationError, match="outside valid range"):
            validate_numeric_range(150, "accuracy_percent")

    def test_valid_coordinates(self):
        """Valid game coordinates should pass."""
        validate_numeric_range(500, "coordinates")
        validate_numeric_range(-500, "coordinates")

    def test_coordinates_out_of_range(self):
        """Coordinates outside game bounds should fail."""
        with pytest.raises(ValidationError, match="outside valid range"):
            validate_numeric_range(15000, "coordinates")


class TestStringValidation:
    """Test string validation."""

    def test_valid_string(self):
        """Alphanumeric string with allowed chars should pass."""
        validate_string_safe("player_001", "unique_id")
        validate_string_safe("build-1.0.2", "build_number")

    def test_string_too_long(self):
        """String exceeding max length should fail."""
        with pytest.raises(ValidationError, match="exceeds max length"):
            validate_string_safe("a" * 300, "unique_id", max_length=255)

    def test_string_with_special_chars(self):
        """String with special characters should fail."""
        with pytest.raises(ValidationError, match="invalid characters"):
            validate_string_safe("player@001", "unique_id")

    def test_string_with_sql_injection(self):
        """String with SQL injection attempt should fail."""
        with pytest.raises(ValidationError, match="invalid characters"):
            validate_string_safe("1'; DROP TABLE events; --", "unique_id")

    def test_string_with_xss(self):
        """String with XSS attempt should fail."""
        with pytest.raises(ValidationError, match="invalid characters"):
            validate_string_safe("<script>alert('xss')</script>", "unique_id")


class TestTimestampValidation:
    """Test timestamp validation."""

    def test_valid_timestamp(self):
        """Valid ISO timestamp should pass."""
        ts = datetime.utcnow().isoformat() + "Z"
        result = validate_timestamp(ts)
        assert isinstance(result, datetime)

    def test_timestamp_with_timezone(self):
        """Timestamp with timezone should pass."""
        ts = "2026-02-16T12:00:00+00:00"
        result = validate_timestamp(ts)
        assert isinstance(result, datetime)

    def test_future_timestamp(self):
        """Timestamp in future should fail."""
        future = (datetime.utcnow() + timedelta(hours=1)).isoformat() + "Z"
        with pytest.raises(ValidationError, match="in the future"):
            validate_timestamp(future)

    def test_invalid_timestamp_format(self):
        """Invalid timestamp format should fail."""
        with pytest.raises(ValidationError, match="Invalid timestamp"):
            validate_timestamp("not-a-timestamp")


class TestEventValidation:
    """Test complete event validation."""

    def test_valid_event(self):
        """Valid event data should pass."""
        event = {
            "event_type": 102,
            "event_subtype": 1,
            "magnitude": 250.5,
            "x": 100,
            "y": 200,
            "z": 0,
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "data": {"level": "1", "score": "100"}
        }
        validate_event_data(event)  # Should not raise

    def test_missing_required_field(self):
        """Event missing required field should fail."""
        event = {
            "magnitude": 250.5,
            # Missing event_type
        }
        with pytest.raises(ValidationError, match="Missing required field"):
            validate_event_data(event)

    def test_invalid_event_type(self):
        """Event type out of range should fail."""
        event = {
            "event_type": 9999,  # Too high
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        with pytest.raises(ValidationError, match="outside valid range"):
            validate_event_data(event)

    def test_invalid_magnitude_for_reaction_time(self):
        """Invalid reaction time magnitude should fail."""
        event = {
            "event_type": 102,  # CORRECT_RESPONSE (expects reaction time)
            "magnitude": 50000,  # 50 seconds - unrealistic
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
        with pytest.raises(ValidationError, match="outside valid range"):
            validate_event_data(event)

    def test_json_data_too_large(self):
        """Event data JSON exceeding size limit should fail."""
        event = {
            "event_type": 100,
            "data": {"huge": "x" * 15000},  # Over 10KB limit
        }
        with pytest.raises(ValidationError, match="exceeds 10KB"):
            validate_event_data(event)

    def test_data_not_json_object(self):
        """Event data not being a dict should fail."""
        event = {
            "event_type": 100,
            "data": "not-a-dict",
        }
        with pytest.raises(ValidationError, match="must be a JSON object"):
            validate_event_data(event)


class TestSessionValidation:
    """Test session validation."""

    def test_valid_session(self):
        """Valid session data should pass."""
        session = {
            "unique_id": "player_001",
            "build_number": "1.0.2"
        }
        validate_session_data(session)  # Should not raise

    def test_invalid_unique_id(self):
        """Invalid unique_id with special chars should fail."""
        session = {
            "unique_id": "player@001",
        }
        with pytest.raises(ValidationError, match="invalid characters"):
            validate_session_data(session)

    def test_unique_id_too_long(self):
        """unique_id exceeding max length should fail."""
        session = {
            "unique_id": "x" * 150,
        }
        with pytest.raises(ValidationError, match="exceeds max length"):
            validate_session_data(session)

    def test_build_number_too_long(self):
        """build_number exceeding max length should fail."""
        session = {
            "build_number": "1." * 30,  # Over 50 chars
        }
        with pytest.raises(ValidationError, match="exceeds max length"):
            validate_session_data(session)


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_zero_magnitude(self):
        """Zero magnitude should be valid."""
        event = {
            "event_type": 100,
            "magnitude": 0,
        }
        validate_event_data(event)  # Should not raise

    def test_exact_max_reaction_time(self):
        """Exactly 10000ms reaction time should pass."""
        event = {
            "event_type": 102,
            "magnitude": 10000,
        }
        validate_event_data(event)  # Should not raise

    def test_empty_data_object(self):
        """Empty data object should be valid."""
        event = {
            "event_type": 100,
            "data": {}
        }
        validate_event_data(event)  # Should not raise

    def test_none_values(self):
        """None values for optional fields should be valid."""
        event = {
            "event_type": 100,
            "event_subtype": None,
            "x": None,
            "y": None,
            "z": None,
            "magnitude": None,
        }
        validate_event_data(event)  # Should not raise


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
