"""JWT handling — token creation and verification with IP binding.

Implements Zero Trust session management per SECURITY.md.
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

from jose import JWTError, jwt

from src.config import settings


class TokenError(Exception):
    """Raised when token verification fails."""


def create_token(
    user_id: str,
    org_id: str,
    role: str,
    ip_address: str,
    expires_delta: timedelta | None = None,
) -> str:
    """Create a JWT access token with IP binding.

    Per SECURITY.md Zero Trust: token contains originating IP,
    reject if request IP differs.
    """
    if expires_delta is None:
        expires_delta = timedelta(minutes=settings.jwt_access_token_expire_minutes)

    now = datetime.now(UTC)
    jwt_id = str(uuid4())

    claims: dict[str, Any] = {
        "sub": user_id,
        "org_id": org_id,
        "role": role,
        "ip": ip_address,
        "jti": jwt_id,
        "iat": now,
        "exp": now + expires_delta,
    }

    return jwt.encode(claims, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def verify_token(token: str, request_ip: str | None = None) -> dict[str, Any]:
    """Verify JWT and optionally check IP binding.

    Returns decoded claims or raises TokenError.
    """
    try:
        claims = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except JWTError as e:
        raise TokenError(f"Invalid token: {e}") from e

    # Check expiration
    exp = claims.get("exp")
    if exp and datetime.fromtimestamp(exp, tz=UTC) < datetime.now(UTC):
        raise TokenError("Token expired")

    # IP binding check (Zero Trust)
    if settings.jwt_ip_binding_enabled and request_ip:
        token_ip = claims.get("ip", "")
        if token_ip and token_ip != request_ip:
            raise TokenError(f"IP mismatch: token bound to {token_ip}, request from {request_ip}")

    return claims
