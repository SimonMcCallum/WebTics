"""Cryptographic utilities for withdrawal codes and privacy."""
import secrets
import hashlib
import hmac
from typing import Tuple


# Secret key for HMAC (MUST be set via environment variable in production)
# This prevents rainbow table attacks on withdrawal codes
SECRET_KEY = "CHANGE_THIS_IN_PRODUCTION_USE_ENV_VAR"  # TODO: Move to .env


def generate_withdrawal_code() -> str:
    """
    Generate a cryptographically secure withdrawal code.

    Format: WC-{uuid}-{uuid}-{uuid}-{uuid}
    Provides 128 bits of entropy (same as UUID4).

    Returns:
        str: Withdrawal code like "WC-7f3a9b2e-4d1c-8a5f-9e2b-3c7d1a8f4e6b"
    """
    # Generate 16 random bytes (128 bits)
    random_bytes = secrets.token_bytes(16)

    # Format as hex with dashes (UUID-like format)
    hex_str = random_bytes.hex()
    formatted = f"{hex_str[0:8]}-{hex_str[8:12]}-{hex_str[12:16]}-{hex_str[16:20]}-{hex_str[20:32]}"

    return f"WC-{formatted}"


def generate_participant_id() -> str:
    """
    Generate a short pseudonymous participant ID.

    Format: P-{random_hex}
    Provides 64 bits of entropy.

    Returns:
        str: Participant ID like "P-a3f8b2c1e5d7f9b4"
    """
    random_bytes = secrets.token_bytes(8)  # 64 bits
    return f"P-{random_bytes.hex()}"


def generate_salt() -> str:
    """
    Generate a random salt for hashing.

    Returns:
        str: 32-character hex salt
    """
    return secrets.token_hex(16)  # 16 bytes = 32 hex characters


def hash_withdrawal_code(withdrawal_code: str, salt: str) -> str:
    """
    Hash a withdrawal code using HMAC-SHA256.

    Uses:
    - HMAC with secret key (prevents rainbow tables)
    - Per-record salt (prevents hash comparison across records)
    - SHA256 (secure hash function)

    Args:
        withdrawal_code: The plaintext withdrawal code
        salt: Random salt for this specific record

    Returns:
        str: 64-character hex hash
    """
    # Combine secret key and salt
    key = f"{SECRET_KEY}:{salt}".encode('utf-8')

    # Compute HMAC
    h = hmac.new(key, withdrawal_code.encode('utf-8'), hashlib.sha256)

    return h.hexdigest()


def verify_withdrawal_code(withdrawal_code: str, salt: str, expected_hash: str) -> bool:
    """
    Verify a withdrawal code against its stored hash.

    Args:
        withdrawal_code: The plaintext code to verify
        salt: The salt used when creating the hash
        expected_hash: The stored hash to compare against

    Returns:
        bool: True if code matches, False otherwise
    """
    computed_hash = hash_withdrawal_code(withdrawal_code, salt)

    # Use constant-time comparison to prevent timing attacks
    return hmac.compare_digest(computed_hash, expected_hash)


def hash_ip_address(ip_address: str) -> str:
    """
    Hash an IP address for privacy-preserving abuse detection.

    Args:
        ip_address: IP address to hash

    Returns:
        str: SHA256 hash of IP address
    """
    return hashlib.sha256(f"{SECRET_KEY}:{ip_address}".encode('utf-8')).hexdigest()


def generate_consent_record() -> Tuple[str, str, str, str]:
    """
    Generate a complete consent record with all cryptographic components.

    Returns:
        Tuple of (withdrawal_code, participant_id, salt, hash)
    """
    withdrawal_code = generate_withdrawal_code()
    participant_id = generate_participant_id()
    salt = generate_salt()
    code_hash = hash_withdrawal_code(withdrawal_code, salt)

    return withdrawal_code, participant_id, salt, code_hash


# Security validation
def validate_secret_key():
    """Validate that the secret key has been changed from default."""
    if SECRET_KEY == "CHANGE_THIS_IN_PRODUCTION_USE_ENV_VAR":
        import warnings
        warnings.warn(
            "CRITICAL SECURITY WARNING: Using default SECRET_KEY. "
            "Set WEBTICS_SECRET_KEY environment variable in production!",
            RuntimeWarning
        )


# Run validation on import
validate_secret_key()
