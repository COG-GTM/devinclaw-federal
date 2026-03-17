"""Session routes — monitor and manage Devin sessions.

GET  /api/v1/sessions          — list active sessions
GET  /api/v1/sessions/{id}     — session detail + messages
POST /api/v1/sessions/{id}/escalate — manually escalate
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel

from src.api.middleware.rbac import get_current_user

router = APIRouter(prefix="/sessions", tags=["sessions"])

# In-memory session store (production: PostgreSQL + session_manager registry)
_sessions_store: dict[str, dict[str, Any]] = {}


class SessionResponse(BaseModel):
    session_id: str
    task_id: str
    status: str
    spoke: str
    skill_name: str
    created_at: str
    updated_at: str


@router.get("")
async def list_sessions(
    request: Request,
    status: str | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> dict[str, Any]:
    """List Devin sessions."""
    claims = get_current_user(request)
    org_id = claims.get("org_id", "")

    filtered = [s for s in _sessions_store.values() if s.get("org_id") == org_id]
    if status:
        filtered = [s for s in filtered if s.get("status") == status]

    filtered.sort(key=lambda s: s.get("created_at", ""), reverse=True)
    total = len(filtered)
    items = filtered[offset : offset + limit]

    return {
        "items": [
            {
                "session_id": s["session_id"],
                "task_id": s.get("task_id", ""),
                "status": s.get("status", "unknown"),
                "spoke": s.get("spoke", ""),
                "skill_name": s.get("skill_name", ""),
                "created_at": s.get("created_at", ""),
            }
            for s in items
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/{session_id}")
async def get_session(request: Request, session_id: str) -> dict[str, Any]:
    """Get session detail including messages."""
    claims = get_current_user(request)
    org_id = claims.get("org_id", "")

    session = _sessions_store.get(session_id)
    if not session or session.get("org_id") != org_id:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "session_id": session["session_id"],
        "task_id": session.get("task_id", ""),
        "status": session.get("status", "unknown"),
        "spoke": session.get("spoke", ""),
        "skill_name": session.get("skill_name", ""),
        "messages": session.get("messages", []),
        "artifacts": session.get("artifacts", []),
        "created_at": session.get("created_at", ""),
        "updated_at": session.get("updated_at", ""),
    }


@router.post("/{session_id}/escalate")
async def escalate_session(request: Request, session_id: str) -> dict[str, str]:
    """Manually escalate a session to human review."""
    claims = get_current_user(request)
    org_id = claims.get("org_id", "")

    session = _sessions_store.get(session_id)
    if not session or session.get("org_id") != org_id:
        raise HTTPException(status_code=404, detail="Session not found")

    session["status"] = "escalated"
    session["updated_at"] = datetime.now(UTC).isoformat()
    session["escalated_by"] = claims.get("sub", "")

    return {"session_id": session_id, "status": "escalated"}
