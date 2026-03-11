"""Password handling — bcrypt hashing and policy enforcement.

STIG V-220629: 14+ character minimum.
NIST AC-7: Lock after 5 failed attempts, 15-minute duration.
"""

from __future__ import annotations

from passlib.context import CryptContext

from src.config import settings

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=12)


class PasswordPolicyError(Exception):
    """Raised when a password does not meet policy requirements."""


def validate_password_policy(password: str) -> None:
    """Enforce password policy per STIG V-220629.

    Requirements:
      - Minimum 14 characters
      - At least one uppercase letter
      - At least one lowercase letter
      - At least one digit
      - At least one special character
    """
    errors: list[str] = []

    if len(password) < settings.min_password_length:
        errors.append(f"Password must be at least {settings.min_password_length} characters")

    if not any(c.isupper() for c in password):
        errors.append("Password must contain at least one uppercase letter")

    if not any(c.islower() for c in password):
        errors.append("Password must contain at least one lowercase letter")

    if not any(c.isdigit() for c in password):
        errors.append("Password must contain at least one digit")

    if not any(c in "!@#$%^&*()_+-=[]{}|;':\",./<>?" for c in password):
        errors.append("Password must contain at least one special character")

    if errors:
        raise PasswordPolicyError("; ".join(errors))


def hash_password(password: str) -> str:
    """Hash a password using bcrypt with 12 rounds."""
    return _pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its bcrypt hash."""
    return _pwd_context.verify(plain_password, hashed_password)
