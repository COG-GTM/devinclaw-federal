"""Memory routes — CRUD and search for the four-scope memory system.

GET    /api/v1/memory          — list memory entries
POST   /api/v1/memory          — create memory entry
GET    /api/v1/memory/search   — semantic search across memory
DELETE /api/v1/memory/{id}     — remove entry
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field

from src.api.middleware.rbac import get_current_user

router = APIRouter(prefix="/memory", tags=["memory"])

# Shared memory manager instance (set during app startup in production)
_memory_manager = None


def get_memory_manager():  # noqa: ANN201
    """Get or create a memory manager instance."""
    global _memory_manager  # noqa: PLW0603
    if _memory_manager is None:
        from src.memory.memory_manager import MemoryManager

        _memory_manager = MemoryManager()
    return _memory_manager


class MemoryCreateRequest(BaseModel):
    scope: str = Field(pattern=r"^(session|user|org|project)$")
    key: str = Field(min_length=1, max_length=500)
    value: str = Field(min_length=1)
    source_session_id: str = ""
    tags: list[str] = Field(default_factory=list)


@router.get("")
async def list_memory(
    request: Request,
    scope: str | None = Query(None, pattern=r"^(session|user|org|project)$"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
) -> dict[str, Any]:
    """List memory entries, optionally filtered by scope."""
    claims = get_current_user(request)
    org_id = claims.get("org_id", "")
    user_id = claims.get("sub", "")

    mm = get_memory_manager()

    if scope:
        scope_id = org_id if scope == "org" else user_id
        entries = mm.get_by_scope(scope=scope, scope_id=scope_id, limit=limit, offset=offset)
    else:
        entries = mm.list_all(limit=limit, offset=offset)

    return {
        "items": [e.to_dict() for e in entries],
        "total": mm.count(),
        "limit": limit,
        "offset": offset,
    }


@router.post("", status_code=201)
async def create_memory(request: Request, body: MemoryCreateRequest) -> dict[str, Any]:
    """Create a new memory entry."""
    claims = get_current_user(request)
    org_id = claims.get("org_id", "")
    user_id = claims.get("sub", "")

    mm = get_memory_manager()

    scope_id = org_id if body.scope in ("org", "project") else user_id
    entry = mm.store(
        scope=body.scope,
        scope_id=scope_id,
        key=body.key,
        value=body.value,
        source_session_id=body.source_session_id,
        tags=body.tags,
    )

    return entry.to_dict()


@router.get("/search")
async def search_memory(
    request: Request,
    q: str = Query(min_length=2, description="Search query"),
    scope: str | None = Query(None, pattern=r"^(session|user|org|project)$"),
    limit: int = Query(10, ge=1, le=50),
) -> dict[str, Any]:
    """Search memory entries by keyword."""
    claims = get_current_user(request)
    org_id = claims.get("org_id", "")

    mm = get_memory_manager()
    results = mm.search(
        query=q,
        scope=scope,
        scope_id=org_id if scope else None,
        limit=limit,
    )

    return {
        "query": q,
        "items": [e.to_dict() for e in results],
        "total": len(results),
    }


@router.delete("/{entry_id}", status_code=204)
async def delete_memory(request: Request, entry_id: str) -> None:
    """Delete a memory entry."""
    get_current_user(request)

    mm = get_memory_manager()
    if not mm.delete(entry_id):
        raise HTTPException(status_code=404, detail="Memory entry not found")
