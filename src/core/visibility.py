"""Visibility Layer — task journey trace, topology, rollups, correlation engine.

Provides the data layer for three dashboard audiences:
  - Dev:  execution detail, session logs, step-by-step trace
  - PM:   velocity metrics, SLA compliance, aggregate rollups
  - CISO: compliance posture, risk heat map, guardrail violations

Section 8 of the DevinClaw Federal architectural specification.
"""

from __future__ import annotations

import logging
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from src.core.oscal_exporter import CONTROL_IMPLEMENTATIONS as _OSCAL_CONTROLS

logger = logging.getLogger("devinclaw.visibility")


# ---------------------------------------------------------------------------
# Task Journey Trace — 12-step orchestration pipeline visibility
# ---------------------------------------------------------------------------

PIPELINE_STEPS: list[str] = [
    "intake",
    "authenticate",
    "route_skill",
    "check_guardrails",
    "select_spoke",
    "determine_arena",
    "inject_memory",
    "launch_sessions",
    "monitor_sessions",
    "validate_sdlc",
    "write_audit",
    "update_memory",
]


@dataclass
class TraceStep:
    """A single step in the task journey trace."""

    step_name: str
    step_index: int
    status: str = "pending"  # pending | in_progress | completed | failed | skipped
    started_at: str = ""
    completed_at: str = ""
    duration_ms: float = 0.0
    detail: dict[str, Any] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)


@dataclass
class TaskTrace:
    """Full task journey trace across all 12 pipeline steps."""

    task_id: str
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    steps: list[TraceStep] = field(default_factory=list)
    current_step: int = 0
    status: str = "running"  # running | completed | failed | blocked | escalated
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.steps:
            self.steps = [
                TraceStep(step_name=name, step_index=i) for i, name in enumerate(PIPELINE_STEPS)
            ]


class TaskTraceManager:
    """Manages task journey traces for visibility into pipeline execution."""

    def __init__(self) -> None:
        self._traces: dict[str, TaskTrace] = {}

    def create_trace(self, task_id: str, metadata: dict[str, Any] | None = None) -> TaskTrace:
        trace = TaskTrace(task_id=task_id, metadata=metadata or {})
        self._traces[task_id] = trace
        return trace

    def start_step(self, task_id: str, step_name: str, detail: dict[str, Any] | None = None) -> None:
        trace = self._traces.get(task_id)
        if not trace:
            return
        for step in trace.steps:
            if step.step_name == step_name:
                step.status = "in_progress"
                step.started_at = datetime.now(UTC).isoformat()
                step.detail = detail or {}
                trace.current_step = step.step_index
                break

    def complete_step(
        self, task_id: str, step_name: str, detail: dict[str, Any] | None = None
    ) -> None:
        trace = self._traces.get(task_id)
        if not trace:
            return
        for step in trace.steps:
            if step.step_name == step_name:
                step.status = "completed"
                step.completed_at = datetime.now(UTC).isoformat()
                if step.started_at:
                    start = datetime.fromisoformat(step.started_at)
                    end = datetime.fromisoformat(step.completed_at)
                    step.duration_ms = (end - start).total_seconds() * 1000
                if detail:
                    step.detail.update(detail)
                break

    def fail_step(self, task_id: str, step_name: str, errors: list[str] | None = None) -> None:
        trace = self._traces.get(task_id)
        if not trace:
            return
        for step in trace.steps:
            if step.step_name == step_name:
                step.status = "failed"
                step.completed_at = datetime.now(UTC).isoformat()
                step.errors = errors or []
                trace.status = "failed"
                break

    def get_trace(self, task_id: str) -> TaskTrace | None:
        return self._traces.get(task_id)

    def list_traces(self, limit: int = 50) -> list[TaskTrace]:
        traces = sorted(self._traces.values(), key=lambda t: t.created_at, reverse=True)
        return traces[:limit]

    def to_dict(self, task_id: str) -> dict[str, Any] | None:
        trace = self._traces.get(task_id)
        if not trace:
            return None
        return {
            "task_id": trace.task_id,
            "created_at": trace.created_at,
            "status": trace.status,
            "current_step": trace.current_step,
            "steps": [
                {
                    "step_name": s.step_name,
                    "step_index": s.step_index,
                    "status": s.status,
                    "started_at": s.started_at,
                    "completed_at": s.completed_at,
                    "duration_ms": s.duration_ms,
                    "detail": s.detail,
                    "errors": s.errors,
                }
                for s in trace.steps
            ],
            "metadata": trace.metadata,
        }


# ---------------------------------------------------------------------------
# Service Topology — real-time service mesh view
# ---------------------------------------------------------------------------


@dataclass
class ServiceNode:
    """A node in the service topology."""

    node_id: str
    name: str
    node_type: str  # api | database | cache | executor | external
    status: str = "healthy"  # healthy | degraded | down | unknown
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class ServiceEdge:
    """A connection between topology nodes."""

    source: str
    target: str
    edge_type: str = "depends_on"  # depends_on | communicates_with | reads_from | writes_to
    latency_ms: float = 0.0
    status: str = "active"  # active | degraded | down


def get_topology() -> dict[str, Any]:
    """Return the current service topology as a graph structure.

    This is a static topology map — in production it would be populated
    from service health checks and tracing data.
    """
    nodes: list[dict[str, Any]] = [
        {"id": "api-server", "name": "DevinClaw API", "type": "api", "status": "healthy", "port": 8420},
        {"id": "dashboard", "name": "Next.js Dashboard", "type": "frontend", "status": "healthy", "port": 3000},
        {"id": "postgres", "name": "PostgreSQL", "type": "database", "status": "healthy", "port": 5432},
        {"id": "redis", "name": "Redis", "type": "cache", "status": "healthy", "port": 6379},
        {"id": "skill-router", "name": "Skill Router", "type": "internal", "status": "healthy"},
        {"id": "guardrail-engine", "name": "Guardrail Engine", "type": "internal", "status": "healthy"},
        {"id": "arena-executor", "name": "Arena Executor", "type": "internal", "status": "healthy"},
        {"id": "audit-writer", "name": "Audit Writer", "type": "internal", "status": "healthy"},
        {"id": "devin-cloud", "name": "Devin Cloud API", "type": "external", "status": "healthy"},
        {"id": "devin-cli", "name": "Devin CLI", "type": "local", "status": "healthy"},
        {"id": "vault", "name": "Secrets Vault", "type": "security", "status": "healthy"},
    ]

    edges: list[dict[str, Any]] = [
        {"source": "dashboard", "target": "api-server", "type": "communicates_with"},
        {"source": "api-server", "target": "postgres", "type": "reads_from"},
        {"source": "api-server", "target": "redis", "type": "reads_from"},
        {"source": "api-server", "target": "skill-router", "type": "depends_on"},
        {"source": "api-server", "target": "guardrail-engine", "type": "depends_on"},
        {"source": "api-server", "target": "arena-executor", "type": "depends_on"},
        {"source": "api-server", "target": "audit-writer", "type": "depends_on"},
        {"source": "api-server", "target": "vault", "type": "depends_on"},
        {"source": "arena-executor", "target": "devin-cloud", "type": "communicates_with"},
        {"source": "arena-executor", "target": "devin-cli", "type": "communicates_with"},
        {"source": "audit-writer", "target": "postgres", "type": "writes_to"},
    ]

    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "nodes": nodes,
        "edges": edges,
        "summary": {
            "total_nodes": len(nodes),
            "healthy_nodes": sum(1 for n in nodes if n["status"] == "healthy"),
            "total_edges": len(edges),
        },
    }


# ---------------------------------------------------------------------------
# Aggregate Rollups — time-series metrics
# ---------------------------------------------------------------------------


class MetricsRollup:
    """Aggregate rollup engine for time-series metrics."""

    def __init__(self) -> None:
        self._task_counts: dict[str, int] = defaultdict(int)  # date -> count
        self._skill_counts: dict[str, int] = defaultdict(int)  # skill_name -> count
        self._guardrail_violations: dict[str, int] = defaultdict(int)  # rule_id -> count
        self._avg_durations: list[float] = []
        self._compliance_scores: list[float] = []

    def record_task(
        self,
        skill_name: str,
        duration_seconds: float,
        guardrail_violations: list[str] | None = None,
        compliance_score: float = 1.0,
    ) -> None:
        today = datetime.now(UTC).strftime("%Y-%m-%d")
        self._task_counts[today] += 1
        self._skill_counts[skill_name] += 1
        self._avg_durations.append(duration_seconds)
        self._compliance_scores.append(compliance_score)
        for rule_id in (guardrail_violations or []):
            self._guardrail_violations[rule_id] += 1

    def get_rollups(self) -> dict[str, Any]:
        total_tasks = sum(self._task_counts.values())
        avg_duration = sum(self._avg_durations) / len(self._avg_durations) if self._avg_durations else 0.0
        avg_compliance = (
            sum(self._compliance_scores) / len(self._compliance_scores) if self._compliance_scores else 1.0
        )

        return {
            "timestamp": datetime.now(UTC).isoformat(),
            "summary": {
                "total_tasks": total_tasks,
                "avg_duration_seconds": round(avg_duration, 2),
                "avg_compliance_score": round(avg_compliance, 4),
                "total_guardrail_violations": sum(self._guardrail_violations.values()),
            },
            "tasks_by_date": dict(sorted(self._task_counts.items())),
            "tasks_by_skill": dict(sorted(self._skill_counts.items(), key=lambda x: x[1], reverse=True)),
            "guardrail_violations": dict(
                sorted(self._guardrail_violations.items(), key=lambda x: x[1], reverse=True)
            ),
        }


# ---------------------------------------------------------------------------
# Correlation Engine — cross-session / cross-task linking
# ---------------------------------------------------------------------------


class CorrelationEngine:
    """Links related events across tasks, sessions, and audit entries."""

    def __init__(self) -> None:
        self._correlations: dict[str, list[dict[str, Any]]] = defaultdict(list)

    def add_event(self, correlation_id: str, event: dict[str, Any]) -> None:
        event.setdefault("timestamp", datetime.now(UTC).isoformat())
        event.setdefault("event_id", str(uuid4()))
        self._correlations[correlation_id].append(event)

    def get_correlated_events(self, correlation_id: str) -> list[dict[str, Any]]:
        events = self._correlations.get(correlation_id, [])
        return sorted(events, key=lambda e: e.get("timestamp", ""))

    def find_related(self, event_id: str) -> list[dict[str, Any]]:
        """Find all events in the same correlation chain as the given event."""
        for corr_id, events in self._correlations.items():
            for ev in events:
                if ev.get("event_id") == event_id:
                    return self.get_correlated_events(corr_id)
        return []

    def correlate(
        self,
        task_id: str,
        session_ids: list[str] | None = None,
        audit_entry_ids: list[str] | None = None,
    ) -> dict[str, Any]:
        """Build a correlation map for a task and its related sessions/audit entries."""
        events = self.get_correlated_events(task_id)
        return {
            "correlation_id": task_id,
            "event_count": len(events),
            "events": events,
            "related_sessions": session_ids or [],
            "related_audit_entries": audit_entry_ids or [],
            "timestamp": datetime.now(UTC).isoformat(),
        }


# ---------------------------------------------------------------------------
# Multi-Audience Dashboard Data
# ---------------------------------------------------------------------------


def get_dev_dashboard(
    trace_manager: TaskTraceManager,
    correlation_engine: CorrelationEngine,
    task_id: str | None = None,
) -> dict[str, Any]:
    """Dev audience: execution detail, session logs, step-by-step trace."""
    data: dict[str, Any] = {
        "audience": "dev",
        "timestamp": datetime.now(UTC).isoformat(),
    }
    if task_id:
        data["trace"] = trace_manager.to_dict(task_id)
        data["correlated_events"] = correlation_engine.get_correlated_events(task_id)
    else:
        traces = trace_manager.list_traces(limit=20)
        data["recent_traces"] = [
            {
                "task_id": t.task_id,
                "status": t.status,
                "current_step": t.current_step,
                "created_at": t.created_at,
            }
            for t in traces
        ]
    return data


def get_pm_dashboard(
    metrics: MetricsRollup,
) -> dict[str, Any]:
    """PM audience: velocity metrics, SLA compliance, aggregate rollups."""
    rollups = metrics.get_rollups()
    return {
        "audience": "pm",
        "timestamp": datetime.now(UTC).isoformat(),
        "velocity": {
            "total_tasks": rollups["summary"]["total_tasks"],
            "avg_duration_seconds": rollups["summary"]["avg_duration_seconds"],
            "tasks_by_date": rollups["tasks_by_date"],
        },
        "sla_compliance": {
            "avg_compliance_score": rollups["summary"]["avg_compliance_score"],
            "guardrail_violation_count": rollups["summary"]["total_guardrail_violations"],
        },
        "skill_utilization": rollups["tasks_by_skill"],
    }


def get_ciso_dashboard(
    metrics: MetricsRollup,
) -> dict[str, Any]:
    """CISO audience: compliance posture, risk heat map, guardrail violations."""
    rollups = metrics.get_rollups()
    return {
        "audience": "ciso",
        "timestamp": datetime.now(UTC).isoformat(),
        "compliance_posture": {
            "avg_score": rollups["summary"]["avg_compliance_score"],
            "frameworks": ["NIST 800-53 Rev 5", "STIG", "FedRAMP Moderate", "EO 14028"],
        },
        "risk_heat_map": {
            "guardrail_violations": rollups["guardrail_violations"],
            "total_violations": rollups["summary"]["total_guardrail_violations"],
        },
        "controls_implemented": len(
            [c for c in _OSCAL_CONTROLS if c["status"] == "implemented"]
        ),
        "controls_partial": len(
            [c for c in _OSCAL_CONTROLS if c["status"] == "partially-implemented"]
        ),
    }
