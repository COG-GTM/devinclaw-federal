"""Schedule routes — create and manage recurring/one-time scheduled tasks.

POST   /api/v1/schedules          — create scheduled task
GET    /api/v1/schedules          — list schedules
DELETE /api/v1/schedules/{id}     — remove schedule
GET    /api/v1/schedules/{id}/runs — run history
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, HTTPException, Query, Request
from pydantic import BaseModel, Field

from src.api.middleware.rbac import get_current_user

router = APIRouter(prefix="/schedules", tags=["schedules"])

# In-memory schedule store
_schedules: dict[str, dict[str, Any]] = {}
_schedule_runs: dict[str, list[dict[str, Any]]] = {}  # schedule_id -> runs


class ScheduleCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=255)
    task_description: str = Field(min_length=5)
    cron_expression: str | None = Field(default=None, description="Cron expression for recurring tasks")
    run_at: str | None = Field(default=None, description="ISO 8601 datetime for one-time tasks")
    webhook_trigger: str | None = Field(default=None, description="Webhook event name to trigger on")
    repos: list[str] = Field(default_factory=list)
    override_skill: str | None = None
    is_active: bool = True


@router.post("", status_code=201)
async def create_schedule(request: Request, body: ScheduleCreateRequest) -> dict[str, Any]:
    """Create a new scheduled task."""
    claims = get_current_user(request)
    org_id = claims.get("org_id", "")
    user_id = claims.get("sub", "")

    schedule_id = str(uuid4())
    now = datetime.now(UTC).isoformat()

    schedule = {
        "id": schedule_id,
        "name": body.name,
        "task_description": body.task_description,
        "cron_expression": body.cron_expression,
        "run_at": body.run_at,
        "webhook_trigger": body.webhook_trigger,
        "repos": body.repos,
        "override_skill": body.override_skill,
        "is_active": body.is_active,
        "user_id": user_id,
        "org_id": org_id,
        "created_at": now,
        "updated_at": now,
        "next_run": body.run_at or "calculated_from_cron",
        "total_runs": 0,
    }
    _schedules[schedule_id] = schedule
    _schedule_runs[schedule_id] = []

    return schedule


@router.get("")
async def list_schedules(
    request: Request,
    is_active: bool | None = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> dict[str, Any]:
    """List all schedules for the current organization."""
    claims = get_current_user(request)
    org_id = claims.get("org_id", "")

    filtered = [s for s in _schedules.values() if s["org_id"] == org_id]
    if is_active is not None:
        filtered = [s for s in filtered if s["is_active"] == is_active]

    filtered.sort(key=lambda s: s["created_at"], reverse=True)
    total = len(filtered)
    items = filtered[offset : offset + limit]

    return {"items": items, "total": total, "limit": limit, "offset": offset}


@router.delete("/{schedule_id}", status_code=204)
async def delete_schedule(request: Request, schedule_id: str) -> None:
    """Remove a schedule."""
    claims = get_current_user(request)
    org_id = claims.get("org_id", "")

    schedule = _schedules.get(schedule_id)
    if not schedule or schedule["org_id"] != org_id:
        raise HTTPException(status_code=404, detail="Schedule not found")

    del _schedules[schedule_id]
    _schedule_runs.pop(schedule_id, None)


@router.get("/{schedule_id}/runs")
async def get_schedule_runs(
    request: Request,
    schedule_id: str,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
) -> dict[str, Any]:
    """Get run history for a schedule."""
    claims = get_current_user(request)
    org_id = claims.get("org_id", "")

    schedule = _schedules.get(schedule_id)
    if not schedule or schedule["org_id"] != org_id:
        raise HTTPException(status_code=404, detail="Schedule not found")

    runs = _schedule_runs.get(schedule_id, [])
    total = len(runs)
    items = runs[offset : offset + limit]

    return {"schedule_id": schedule_id, "items": items, "total": total, "limit": limit, "offset": offset}
