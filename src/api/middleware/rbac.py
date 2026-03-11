"""RBAC middleware — role-based access control decorators.

Provides @require_role decorators and per-endpoint RBAC rules.
Org-scoped data access ensures users only see their organization's data.
"""

from __future__ import annotations

import functools
from collections.abc import Callable
from typing import Any

from fastapi import HTTPException, Request

from src.api.middleware.zero_trust import verify_session_token


def get_current_user(request: Request) -> dict[str, Any]:
    """Extract authenticated user from request.

    Returns claims dict with sub, org_id, role, ip, jti.
    Raises 401 if not authenticated.
    """
    claims = verify_session_token(request)
    if not claims:
        raise HTTPException(status_code=401, detail="Authentication required")
    return claims


def require_role(*allowed_roles: str) -> Callable:
    """Decorator factory for role-based access control.

    Usage:
        @require_role("admin", "engineer")
        async def my_endpoint(request: Request):
            ...
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Find request in args/kwargs
            request: Request | None = None
            for arg in args:
                if isinstance(arg, Request):
                    request = arg
                    break
            if request is None:
                request = kwargs.get("request")
            if request is None:
                raise HTTPException(status_code=500, detail="Request not found in handler arguments")

            claims = get_current_user(request)
            user_role = claims.get("role", "")

            if user_role not in allowed_roles:
                raise HTTPException(
                    status_code=403,
                    detail=f"Role '{user_role}' not authorized. Required: {', '.join(allowed_roles)}",
                )

            # Attach claims to request state for downstream use
            request.state.user_claims = claims
            return await func(*args, **kwargs)

        return wrapper

    return decorator


def get_org_id(request: Request) -> str:
    """Extract org_id from authenticated request for data scoping."""
    claims = getattr(request.state, "user_claims", None)
    if not claims:
        claims = get_current_user(request)
    return claims.get("org_id", "")


def get_user_id(request: Request) -> str:
    """Extract user_id from authenticated request."""
    claims = getattr(request.state, "user_claims", None)
    if not claims:
        claims = get_current_user(request)
    return claims.get("sub", "")
