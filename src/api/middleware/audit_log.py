"""Audit Log middleware — logs every request for compliance.

Structured JSON format per NIST AU-3:
  timestamp, user_id, ip_address, action, outcome, correlation_id
"""

from __future__ import annotations

import logging
import time
from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

from src.api.middleware.zero_trust import get_client_ip

logger = logging.getLogger("devinclaw.audit_log")


class AuditLogMiddleware(BaseHTTPMiddleware):
    """Log every HTTP request for audit trail compliance."""

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid4()))
        request.state.correlation_id = correlation_id

        client_ip = get_client_ip(request)
        method = request.method
        path = request.url.path

        start_time = time.time()

        try:
            response = await call_next(request)
            elapsed = time.time() - start_time

            # Extract user_id if authenticated
            user_id = "anonymous"
            claims = getattr(request.state, "user_claims", None)
            if claims:
                user_id = claims.get("sub", "anonymous")

            logger.info(
                "AUDIT: correlation_id=%s user_id=%s ip=%s method=%s path=%s status=%d duration=%.3fs",
                correlation_id,
                user_id,
                client_ip,
                method,
                path,
                response.status_code,
                elapsed,
            )

            response.headers["X-Correlation-ID"] = correlation_id
            return response

        except Exception:
            elapsed = time.time() - start_time
            logger.error(
                "AUDIT: correlation_id=%s ip=%s method=%s path=%s status=500 duration=%.3fs",
                correlation_id,
                client_ip,
                method,
                path,
                elapsed,
            )
            raise
