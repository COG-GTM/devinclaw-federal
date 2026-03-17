"""Visibility routes — task trace, topology, rollups, correlation, multi-audience dashboards.

GET /api/v1/visibility/topology    — service mesh graph
GET /api/v1/visibility/trace/{id}  — task journey trace
GET /api/v1/visibility/rollups     — aggregate metrics
POST /api/v1/visibility/correlate  — correlation engine query
GET /api/v1/visibility/dashboard/dev   — dev audience
GET /api/v1/visibility/dashboard/pm    — PM audience
GET /api/v1/visibility/dashboard/ciso  — CISO audience
"""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from src.core.visibility import (
    CorrelationEngine,
    MetricsRollup,
    TaskTraceManager,
    get_ciso_dashboard,
    get_dev_dashboard,
    get_pm_dashboard,
    get_topology,
)

logger = logging.getLogger("devinclaw.visibility_routes")

router = APIRouter(prefix="/api/v1/visibility", tags=["visibility"])

# Singletons — in production these would be injected via dependency injection
_trace_manager = TaskTraceManager()
_metrics = MetricsRollup()
_correlation_engine = CorrelationEngine()


def get_trace_manager() -> TaskTraceManager:
    return _trace_manager


def get_metrics_rollup() -> MetricsRollup:
    return _metrics


def get_correlation_engine() -> CorrelationEngine:
    return _correlation_engine


# --- Schemas ---
class CorrelateRequest(BaseModel):
    task_id: str = Field(description="Task ID to correlate")
    session_ids: list[str] = Field(default_factory=list)
    audit_entry_ids: list[str] = Field(default_factory=list)


# --- Routes ---
@router.get("/topology")
async def topology() -> dict[str, Any]:
    """Service topology — real-time service mesh view."""
    return get_topology()


@router.get("/trace/{task_id}")
async def task_trace(task_id: str) -> dict[str, Any]:
    """Task journey trace — 12-step pipeline visibility."""
    trace = _trace_manager.to_dict(task_id)
    if trace is None:
        raise HTTPException(status_code=404, detail=f"No trace found for task {task_id}")
    return trace


@router.get("/traces")
async def list_traces(limit: int = Query(default=50, ge=1, le=200)) -> dict[str, Any]:
    """List recent task traces."""
    traces = _trace_manager.list_traces(limit=limit)
    return {
        "count": len(traces),
        "traces": [
            {
                "task_id": t.task_id,
                "status": t.status,
                "current_step": t.current_step,
                "created_at": t.created_at,
            }
            for t in traces
        ],
    }


@router.get("/rollups")
async def rollups() -> dict[str, Any]:
    """Aggregate metrics rollups — time-series data."""
    return _metrics.get_rollups()


@router.post("/correlate")
async def correlate(body: CorrelateRequest) -> dict[str, Any]:
    """Correlation engine — link related events across tasks/sessions."""
    return _correlation_engine.correlate(
        task_id=body.task_id,
        session_ids=body.session_ids,
        audit_entry_ids=body.audit_entry_ids,
    )


@router.get("/dashboard/dev")
async def dev_dashboard(task_id: str | None = Query(default=None)) -> dict[str, Any]:
    """Dev audience dashboard — execution detail, traces, logs."""
    return get_dev_dashboard(_trace_manager, _correlation_engine, task_id)


@router.get("/dashboard/pm")
async def pm_dashboard() -> dict[str, Any]:
    """PM audience dashboard — velocity, SLA compliance, rollups."""
    return get_pm_dashboard(_metrics)


@router.get("/dashboard/ciso")
async def ciso_dashboard() -> dict[str, Any]:
    """CISO audience dashboard — compliance posture, risk, guardrails."""
    return get_ciso_dashboard(_metrics)
