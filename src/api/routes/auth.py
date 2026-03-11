"""Auth routes — registration, login, logout, API key management.

POST /auth/register
POST /auth/login
POST /auth/logout
GET  /auth/me
POST /auth/api-keys
DELETE /auth/api-keys/{id}
"""

from __future__ import annotations

import hashlib
import logging
from datetime import UTC, datetime, timedelta
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel, EmailStr, Field

from src.api.middleware.rbac import get_current_user
from src.api.middleware.zero_trust import get_client_ip
from src.auth.jwt import create_token
from src.auth.passwords import PasswordPolicyError, hash_password, validate_password_policy, verify_password
from src.config import settings

logger = logging.getLogger("devinclaw.auth")

router = APIRouter(prefix="/auth", tags=["auth"])

# In-memory stores (production would use PostgreSQL)
_users: dict[str, dict[str, Any]] = {}  # user_id -> user data
_users_by_email: dict[str, str] = {}  # email -> user_id
_orgs: dict[str, dict[str, Any]] = {}  # org_id -> org data
_api_keys: dict[str, dict[str, Any]] = {}  # key_id -> key data
_sessions: dict[str, dict[str, Any]] = {}  # jwt_id -> session data


# --- Schemas ---
class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=14)
    org_name: str = Field(min_length=2, max_length=255)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class APIKeyCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    scopes: str = "*"
    expires_in_days: int = Field(default=90, ge=1, le=365)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


# --- Routes ---
@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(request: Request, body: RegisterRequest) -> TokenResponse:
    """Register a new user and organization."""
    # Check duplicate email
    if body.email in _users_by_email:
        raise HTTPException(status_code=409, detail="Email already registered")

    # Validate password policy (STIG V-220629)
    try:
        validate_password_policy(body.password)
    except PasswordPolicyError as e:
        raise HTTPException(status_code=422, detail=str(e)) from e

    # Create organization
    org_id = str(uuid4())
    _orgs[org_id] = {
        "id": org_id,
        "name": body.org_name,
        "created_at": datetime.now(UTC).isoformat(),
    }

    # Create user
    user_id = str(uuid4())
    _users[user_id] = {
        "id": user_id,
        "email": body.email,
        "password_hash": hash_password(body.password),
        "org_id": org_id,
        "role": "admin",  # First user is admin
        "is_active": True,
        "failed_login_attempts": 0,
        "locked_until": None,
        "created_at": datetime.now(UTC).isoformat(),
        "last_login": datetime.now(UTC).isoformat(),
    }
    _users_by_email[body.email] = user_id

    # Create token
    client_ip = get_client_ip(request)
    token = create_token(user_id=user_id, org_id=org_id, role="admin", ip_address=client_ip)

    return TokenResponse(
        access_token=token,
        expires_in=settings.jwt_access_token_expire_minutes * 60,
    )


@router.post("/login", response_model=TokenResponse)
async def login(request: Request, body: LoginRequest) -> TokenResponse:
    """Authenticate and return JWT."""
    user_id = _users_by_email.get(body.email)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user = _users[user_id]

    # Check account lockout (NIST AC-7)
    locked_until = user.get("locked_until")
    if locked_until and datetime.fromisoformat(locked_until) > datetime.now(UTC):
        raise HTTPException(status_code=423, detail="Account locked. Try again later.")

    # Verify password
    if not verify_password(body.password, user["password_hash"]):
        user["failed_login_attempts"] = user.get("failed_login_attempts", 0) + 1

        if user["failed_login_attempts"] >= settings.max_failed_login_attempts:
            user["locked_until"] = (
                datetime.now(UTC) + timedelta(minutes=settings.lockout_duration_minutes)
            ).isoformat()
            logger.warning("Account locked for user %s after %d failed attempts", body.email, user["failed_login_attempts"])

        raise HTTPException(status_code=401, detail="Invalid credentials")

    # Reset failed attempts on success
    user["failed_login_attempts"] = 0
    user["locked_until"] = None
    user["last_login"] = datetime.now(UTC).isoformat()

    # Create token
    client_ip = get_client_ip(request)
    token = create_token(
        user_id=user_id,
        org_id=user["org_id"],
        role=user["role"],
        ip_address=client_ip,
    )

    return TokenResponse(
        access_token=token,
        expires_in=settings.jwt_access_token_expire_minutes * 60,
    )


@router.post("/logout", status_code=204)
async def logout(request: Request) -> None:
    """Invalidate the current session."""
    claims = get_current_user(request)
    jwt_id = claims.get("jti", "")
    if jwt_id and jwt_id in _sessions:
        _sessions[jwt_id]["is_active"] = False
    # In production, add to JWT blacklist / revocation list


@router.get("/me")
async def get_me(request: Request) -> dict[str, Any]:
    """Get current user profile."""
    claims = get_current_user(request)
    user_id = claims.get("sub", "")
    user = _users.get(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return {
        "id": user["id"],
        "email": user["email"],
        "org_id": user["org_id"],
        "role": user["role"],
        "is_active": user["is_active"],
        "created_at": user["created_at"],
        "last_login": user["last_login"],
    }


@router.post("/api-keys", status_code=201)
async def create_api_key(request: Request, body: APIKeyCreateRequest) -> dict[str, Any]:
    """Create a new API key."""
    claims = get_current_user(request)
    user_id = claims.get("sub", "")
    org_id = claims.get("org_id", "")

    # Generate key
    raw_key = f"dcf_{uuid4().hex}"
    key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
    key_id = str(uuid4())

    _api_keys[key_id] = {
        "id": key_id,
        "key_hash": key_hash,
        "name": body.name,
        "user_id": user_id,
        "org_id": org_id,
        "scopes": body.scopes,
        "is_active": True,
        "created_at": datetime.now(UTC).isoformat(),
        "expires_at": (datetime.now(UTC) + timedelta(days=body.expires_in_days)).isoformat(),
    }

    return {
        "id": key_id,
        "key": raw_key,  # Only returned once at creation
        "name": body.name,
        "scopes": body.scopes,
        "expires_at": _api_keys[key_id]["expires_at"],
    }


@router.delete("/api-keys/{key_id}", status_code=204)
async def revoke_api_key(request: Request, key_id: str) -> None:
    """Revoke an API key."""
    claims = get_current_user(request)
    org_id = claims.get("org_id", "")

    key = _api_keys.get(key_id)
    if not key or key["org_id"] != org_id:
        raise HTTPException(status_code=404, detail="API key not found")

    key["is_active"] = False
