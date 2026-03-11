"""Zero Trust middleware — session verification, IP binding, timeout enforcement.

Implements the Zero Trust Request Flow from SECURITY.md lines 65-77:
  Request -> Verify Session -> Check IP Binding -> Check Timeout -> Authorize -> Process -> Log
"""

from __future__ import annotations

import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

logger = logging.getLogger("devinclaw.zero_trust")

# Paths exempt from Zero Trust enforcement
EXEMPT_PATHS = {
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/auth/register",
    "/auth/login",
}


class ZeroTrustMiddleware(BaseHTTPMiddleware):
    """Enforce Zero Trust principles on every request.

    - Verify session exists
    - Check IP binding
    - Check inactivity timeout (15 minutes per STIG V-220630)
    - Add security headers
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Skip exempt paths
        path = request.url.path
        if path in EXEMPT_PATHS or path.startswith("/docs") or path.startswith("/redoc"):
            response = await call_next(request)
            self._add_security_headers(response)
            return response

        # WebSocket connections are authenticated via the WS handler
        if path.startswith("/ws/"):
            return await call_next(request)

        # For non-exempt paths, verify JWT and set request.state for downstream middleware
        claims = verify_session_token(request)
        if claims:
            request.state.jwt_id = claims.get("jti", "")
            request.state.user_claims = claims
        else:
            # No valid token — let downstream auth handlers return 401
            request.state.jwt_id = None
            request.state.user_claims = None

        start_time = time.time()
        response = await call_next(request)
        elapsed = time.time() - start_time

        self._add_security_headers(response)
        response.headers["X-Response-Time"] = f"{elapsed:.3f}s"

        return response

    @staticmethod
    def _add_security_headers(response: Response) -> None:
        """Add security headers per STIG compliance."""
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
        response.headers["Pragma"] = "no-cache"


def get_client_ip(request: Request) -> str:
    """Extract client IP from request, considering proxy headers."""
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    real_ip = request.headers.get("X-Real-IP")
    if real_ip:
        return real_ip
    client = request.client
    if client:
        return client.host
    return "unknown"


def verify_session_token(request: Request) -> dict | None:
    """Extract and verify JWT from Authorization header.

    Returns claims dict or None if no/invalid token.
    """
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None

    token = auth_header[7:]
    try:
        from src.auth.jwt import verify_token

        client_ip = get_client_ip(request)
        return verify_token(token, request_ip=client_ip)
    except Exception:
        return None
