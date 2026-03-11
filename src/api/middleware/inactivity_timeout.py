"""Inactivity Timeout Middleware — STIG V-220630 compliance.

Tracks last activity per authenticated session and rejects requests
when the session has been idle for longer than the configured timeout
(default: 15 minutes).

Unlike expiry-based JWT timeout, this middleware resets the timer on
every successful request, enforcing *inactivity*-based session control.
"""

from __future__ import annotations

import logging
import time
from collections import defaultdict

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

from src.config import settings

logger = logging.getLogger("devinclaw.inactivity_timeout")

# In-memory last-activity tracker: jwt_id -> unix timestamp
_last_activity: dict[str, float] = defaultdict(float)

# Paths that do NOT require activity tracking (public endpoints)
_EXEMPT_PATHS: set[str] = {
    "/health",
    "/auth/login",
    "/auth/register",
    "/docs",
    "/openapi.json",
    "/redoc",
}


def update_activity(jwt_id: str) -> None:
    """Record current time as last activity for a session."""
    _last_activity[jwt_id] = time.time()


def clear_activity(jwt_id: str) -> None:
    """Remove activity tracking for a session (logout / expiry)."""
    _last_activity.pop(jwt_id, None)


def get_idle_seconds(jwt_id: str) -> float:
    """Return how many seconds since last activity.  -1 if no record."""
    last = _last_activity.get(jwt_id)
    if last is None:
        return -1.0
    return time.time() - last


class InactivityTimeoutMiddleware(BaseHTTPMiddleware):
    """Reject requests from sessions idle longer than the timeout.

    STIG V-220630: 15-minute inactivity timeout.
    """

    def __init__(self, app: object, timeout_minutes: int | None = None) -> None:
        super().__init__(app)  # type: ignore[arg-type]
        self.timeout_seconds = (timeout_minutes or settings.jwt_access_token_expire_minutes) * 60

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Skip exempt paths
        path = request.url.path.rstrip("/")
        if path in _EXEMPT_PATHS or path.startswith("/ws/"):
            return await call_next(request)

        # Extract JWT ID from request state (set by zero_trust middleware)
        jwt_id: str | None = getattr(request.state, "jwt_id", None)
        if not jwt_id:
            # No auth context — let downstream handle 401
            return await call_next(request)

        # Check inactivity
        idle = get_idle_seconds(jwt_id)
        if idle > self.timeout_seconds:
            logger.warning(
                "Session %s timed out after %.0f seconds of inactivity (limit: %d)",
                jwt_id,
                idle,
                self.timeout_seconds,
            )
            clear_activity(jwt_id)
            return JSONResponse(
                status_code=440,  # Login Timeout (IIS convention, widely understood)
                content={
                    "detail": "Session timed out due to inactivity (STIG V-220630)",
                    "idle_seconds": round(idle),
                    "timeout_seconds": self.timeout_seconds,
                },
            )

        # Update last activity
        update_activity(jwt_id)
        return await call_next(request)
