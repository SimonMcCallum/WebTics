"""
Structured logging configuration for WebTics.
Provides JSON-formatted logs for production and human-readable logs for development.
"""

import logging
import sys
import json
from datetime import datetime, timezone
from typing import Any, Dict
import os
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path


class JSONFormatter(logging.Formatter):
    """
    Format log records as JSON for structured logging.
    Makes logs easy to parse, search, and analyze.
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON string."""

        # Base log data
        log_data: Dict[str, Any] = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = {
                "type": record.exc_info[0].__name__ if record.exc_info[0] else None,
                "message": str(record.exc_info[1]) if record.exc_info[1] else None,
                "traceback": self.formatException(record.exc_info) if record.exc_info else None,
            }

        # Add custom fields from extra parameter
        # Example: logger.info("Message", extra={"user_id": "123", "request_id": "abc"})
        custom_fields = ["user_id", "request_id", "client_id", "session_id",
                        "event_type", "ip_address", "api_key_hash"]
        for field in custom_fields:
            if hasattr(record, field):
                log_data[field] = getattr(record, field)

        # Add process and thread info for debugging
        log_data["process_id"] = record.process
        log_data["thread_id"] = record.thread

        return json.dumps(log_data)


class ColoredFormatter(logging.Formatter):
    """
    Colored console formatter for development.
    Makes logs easier to read during development.
    """

    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[36m",  # Cyan
        "INFO": "\033[32m",  # Green
        "WARNING": "\033[33m",  # Yellow
        "ERROR": "\033[31m",  # Red
        "CRITICAL": "\033[35m",  # Magenta
    }
    RESET = "\033[0m"
    BOLD = "\033[1m"

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors for terminal."""

        # Get color for log level
        color = self.COLORS.get(record.levelname, self.RESET)

        # Format timestamp
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")

        # Format message
        log_msg = (
            f"{color}{self.BOLD}[{record.levelname}]{self.RESET} "
            f"{timestamp} - "
            f"{color}{record.name}{self.RESET} - "
            f"{record.getMessage()}"
        )

        # Add exception info if present
        if record.exc_info:
            log_msg += f"\n{self.formatException(record.exc_info)}"

        return log_msg


def setup_logging(
    level: str = "INFO",
    log_dir: str = "/var/log/webtics",
    use_json: bool = True,
    enable_file_logging: bool = True,
) -> logging.Logger:
    """
    Configure application-wide logging.

    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_dir: Directory for log files (created if doesn't exist)
        use_json: Use JSON formatter (True for production, False for development)
        enable_file_logging: Write logs to files (disable for containers using stdout)

    Returns:
        Configured root logger
    """

    # Parse log level
    log_level = getattr(logging, level.upper(), logging.INFO)

    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level)

    # Remove existing handlers
    root_logger.handlers.clear()

    # Console handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)

    # Choose formatter based on environment
    if use_json:
        console_handler.setFormatter(JSONFormatter())
    else:
        console_handler.setFormatter(ColoredFormatter())

    root_logger.addHandler(console_handler)

    # File handlers (if enabled)
    if enable_file_logging:
        # Create log directory if it doesn't exist
        log_path = Path(log_dir)
        try:
            log_path.mkdir(parents=True, exist_ok=True)
        except PermissionError:
            # Fallback to ./logs if /var/log/webtics not writable
            log_path = Path("./logs")
            log_path.mkdir(parents=True, exist_ok=True)
            root_logger.warning(f"Using fallback log directory: {log_path.absolute()}")

        # Application log (all levels)
        app_log_file = log_path / "app.log"
        app_handler = TimedRotatingFileHandler(
            app_log_file,
            when="midnight",
            interval=1,
            backupCount=30,  # Keep 30 days
            encoding="utf-8",
        )
        app_handler.setLevel(log_level)
        app_handler.setFormatter(JSONFormatter() if use_json else logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        ))
        root_logger.addHandler(app_handler)

        # Error log (errors and above)
        error_log_file = log_path / "error.log"
        error_handler = TimedRotatingFileHandler(
            error_log_file,
            when="midnight",
            interval=1,
            backupCount=90,  # Keep 90 days for errors
            encoding="utf-8",
        )
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(JSONFormatter() if use_json else logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        ))
        root_logger.addHandler(error_handler)

        # Security log (authentication, rate limiting, etc.)
        security_log_file = log_path / "security.log"
        security_handler = TimedRotatingFileHandler(
            security_log_file,
            when="midnight",
            interval=1,
            backupCount=365,  # Keep 1 year for security events
            encoding="utf-8",
        )
        security_handler.setLevel(logging.WARNING)
        security_handler.setFormatter(JSONFormatter())

        # Create security logger
        security_logger = logging.getLogger("webtics.security")
        security_logger.addHandler(security_handler)

    return root_logger


def get_logger(name: str) -> logging.Logger:
    """Get logger for specific module."""
    return logging.getLogger(name)


def log_security_event(event_type: str, details: Dict[str, Any], level: str = "WARNING"):
    """
    Log security-related events to separate security log.

    Args:
        event_type: Type of security event (e.g., "auth_failure", "rate_limit_exceeded")
        details: Additional context (IP, user, endpoint, etc.)
        level: Log level (WARNING, ERROR, CRITICAL)
    """
    security_logger = logging.getLogger("webtics.security")

    log_level = getattr(logging, level.upper(), logging.WARNING)

    security_logger.log(
        log_level,
        f"Security event: {event_type}",
        extra={
            "event_type": event_type,
            **details
        }
    )


# Convenience function for development
def configure_dev_logging():
    """Configure logging for development (colored, DEBUG level)."""
    return setup_logging(
        level="DEBUG",
        log_dir="./logs",
        use_json=False,
        enable_file_logging=True,
    )


# Convenience function for production
def configure_prod_logging():
    """Configure logging for production (JSON, INFO level, stdout)."""
    return setup_logging(
        level=os.getenv("LOG_LEVEL", "INFO"),
        log_dir="/var/log/webtics",
        use_json=True,
        enable_file_logging=bool(os.getenv("ENABLE_FILE_LOGGING", "false").lower() == "true"),
    )
