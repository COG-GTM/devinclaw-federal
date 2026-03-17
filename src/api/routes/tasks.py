"""Task routes — submit, monitor, and manage orchestration tasks.

POST /api/v1/tasks          — submit task (natural language)
GET  /api/v1/tasks/{id}     — task status + audit trail
GET  /api/v1/tasks/{id}/guardrails — guardrail evaluation results
POST /api/v1/tasks/{id}/cancel — cancel task
GET  /api/v1/tasks          — list tasks (paginated)
"""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field

from src.api.middleware.rbac import get_current_user

logger = logging.getLogger("devinclaw.routes.tasks")

router = APIRouter(prefix="/tasks", tags=["tasks"])

# In-memory task store (production: PostgreSQL)
_tasks: dict[str, dict[str, Any]] = {}


class TaskCreateRequest(BaseModel):
    description: str = Field(min_length=5, description="Natural language task description")
    repos: list[str] = Field(default_factory=list)
    override_skill: str | None = None
    override_arena_mode: str | None = None
    is_safety_critical: bool = False
    batch_size: int = Field(default=1, ge=1)
    metadata: dict[str, Any] = Field(default_factory=dict)


class TaskResponse(BaseModel):
    task_id: str
    status: str
    description: str
    skill_name: str | None = None
    spoke: str | None = None
    arena_mode: str | None = None
    session_ids: list[str] = Field(default_factory=list)
    created_at: str
    updated_at: str


@router.post("", response_model=TaskResponse, status_code=201)
async def create_task(request: Request, body: TaskCreateRequest) -> TaskResponse:
    """Submit a new task for orchestration."""
    claims = get_current_user(request)
    user_id = claims.get("sub", "")
    org_id = claims.get("org_id", "")

    task_id = str(uuid4())
    now = datetime.now(UTC).isoformat()

    task = {
        "task_id": task_id,
        "status": "queued",
        "description": body.description,
        "user_id": user_id,
        "org_id": org_id,
        "repos": body.repos,
        "override_skill": body.override_skill,
        "override_arena_mode": body.override_arena_mode,
        "is_safety_critical": body.is_safety_critical,
        "batch_size": body.batch_size,
        "metadata": body.metadata,
        "skill_name": None,
        "spoke": None,
        "arena_mode": None,
        "session_ids": [],
        "guardrail_results": [],
        "sdlc_result": {},
        "artifacts": [],
        "errors": [],
        "created_at": now,
        "updated_at": now,
    }
    _tasks[task_id] = task

    logger.info("Task %s created by user %s: %s", task_id, user_id, body.description[:100])

    return TaskResponse(
        task_id=task_id,
        status="queued",
        description=body.description,
        created_at=now,
        updated_at=now,
    )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(request: Request, task_id: str) -> TaskResponse:
    """Get task status and details."""
    claims = get_current_user(request)
    org_id = claims.get("org_id", "")

    task = _tasks.get(task_id)
    if not task or task["org_id"] != org_id:
        raise HTTPException(status_code=404, detail="Task not found")

    return TaskResponse(
        task_id=task["task_id"],
        status=task["status"],
        description=task["description"],
        skill_name=task.get("skill_name"),
        spoke=task.get("spoke"),
        arena_mode=task.get("arena_mode"),
        session_ids=task.get("session_ids", []),
        created_at=task["created_at"],
        updated_at=task["updated_at"],
    )


@router.get("/{task_id}/guardrails")
async def get_task_guardrails(request: Request, task_id: str) -> dict[str, Any]:
    """Get guardrail evaluation results for a task."""
    claims = get_current_user(request)
    org_id = claims.get("org_id", "")

    task = _tasks.get(task_id)
    if not task or task["org_id"] != org_id:
        raise HTTPException(status_code=404, detail="Task not found")

    return {
        "task_id": task_id,
        "guardrail_results": task.get("guardrail_results", []),
    }


@router.post("/{task_id}/cancel", status_code=200)
async def cancel_task(request: Request, task_id: str) -> dict[str, str]:
    """Cancel a running task."""
    claims = get_current_user(request)
    org_id = claims.get("org_id", "")

    task = _tasks.get(task_id)
    if not task or task["org_id"] != org_id:
        raise HTTPException(status_code=404, detail="Task not found")

    if task["status"] in ("completed", "failed", "cancelled"):
        raise HTTPException(status_code=409, detail=f"Task already in terminal state: {task['status']}")

    task["status"] = "cancelled"
    task["updated_at"] = datetime.now(UTC).isoformat()

    return {"task_id": task_id, "status": "cancelled"}


@router.get("")
async def list_tasks(
    request: Request,
    status: str | None = Query(None, description="Filter by status"),
    skill: str | None = Query(None, description="Filter by skill name"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> dict[str, Any]:
    """List tasks with pagination and filtering."""
    claims = get_current_user(request)
    org_id = claims.get("org_id", "")

    filtered = [t for t in _tasks.values() if t["org_id"] == org_id]

    if status:
        filtered = [t for t in filtered if t["status"] == status]
    if skill:
        filtered = [t for t in filtered if t.get("skill_name") == skill]

    # Sort by created_at descending
    filtered.sort(key=lambda t: t["created_at"], reverse=True)

    total = len(filtered)
    items = filtered[offset : offset + limit]

    return {
        "items": [
            {
                "task_id": t["task_id"],
                "status": t["status"],
                "description": t["description"],
                "skill_name": t.get("skill_name"),
                "created_at": t["created_at"],
            }
            for t in items
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
    }
