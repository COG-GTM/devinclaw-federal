"""Unified Schema Registry — single source of truth for all core data models.

Re-exports all core types and provides JSON Schema generation for each model.
This ensures API consumers, compliance tooling, and documentation all reference
the same canonical definitions.
"""

from __future__ import annotations

from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, Field

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class TaskStatus(StrEnum):
    """Lifecycle states for an orchestration task."""

    QUEUED = "queued"
    ROUTING = "routing"
    GUARDRAIL_CHECK = "guardrail_check"
    EXECUTING = "executing"
    VALIDATING = "validating"
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"
    ESCALATED = "escalated"
    CANCELLED = "cancelled"


class RiskLevel(StrEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ArenaMode(StrEnum):
    SINGLE_RUN = "single-run"
    ARENA_RUN = "arena-run"


class SpokeType(StrEnum):
    CLOUD = "devin-cloud"
    CLI = "devin-cli"
    API = "devin-api"
    REVIEW = "devin-review"
    IDE = "devin-ide"


class SDLCPhase(StrEnum):
    DISCOVERY = "discovery"
    SPECIFICATION = "specification"
    IMPLEMENTATION = "implementation"
    TESTING = "testing"
    REVIEW = "review"
    GOVERNANCE = "governance"
    KNOWLEDGE = "knowledge"


# ---------------------------------------------------------------------------
# Core Schemas (Pydantic v2 — JSON Schema exportable)
# ---------------------------------------------------------------------------


class TaskSchema(BaseModel):
    """Canonical Task schema — every orchestrated unit of work."""

    task_id: str = Field(description="UUID v4 identifier")
    description: str = Field(min_length=5, description="Natural language task description")
    status: TaskStatus = Field(default=TaskStatus.QUEUED)
    user_id: str = Field(description="ID of the requesting user")
    org_id: str = Field(description="Tenant organization ID")
    skill_name: str | None = Field(default=None, description="Routed skill name")
    spoke: SpokeType | None = Field(default=None, description="Selected execution spoke")
    arena_mode: ArenaMode = Field(default=ArenaMode.SINGLE_RUN)
    session_ids: list[str] = Field(default_factory=list)
    repos: list[str] = Field(default_factory=list, description="Target repositories")
    is_safety_critical: bool = Field(default=False, description="DO-178C flag")
    batch_size: int = Field(default=1, ge=1)
    guardrail_results: list[dict[str, Any]] = Field(default_factory=list)
    sdlc_result: dict[str, Any] = Field(default_factory=dict)
    artifacts: list[dict[str, Any]] = Field(default_factory=list)
    errors: list[str] = Field(default_factory=list)
    evidence_pack_path: str = Field(default="")
    metadata: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(description="ISO-8601 creation timestamp")
    updated_at: datetime = Field(description="ISO-8601 last update timestamp")
    duration_seconds: float = Field(default=0.0)

    model_config = {"json_schema_extra": {"title": "DevinClaw Task"}}


class SkillSchema(BaseModel):
    """Canonical Skill schema — a routable capability definition."""

    skill_id: str = Field(description="Unique skill identifier")
    name: str = Field(description="Hyphenated skill name (e.g. plsql-migration)")
    path: str = Field(default="", description="Filesystem path to SKILL.md")
    description: str = Field(description="Human-readable description")
    triggers: list[str] = Field(description="Natural-language trigger phrases")
    sdlc_phase: SDLCPhase = Field(description="Primary SDLC phase")
    risk_level: RiskLevel = Field(default=RiskLevel.MEDIUM)
    default_arena_mode: ArenaMode = Field(default=ArenaMode.SINGLE_RUN)
    arena_sessions: int = Field(default=1, ge=1, le=5)
    mcp_required: list[str] = Field(default_factory=list)
    spokes: list[SpokeType] = Field(default_factory=list)
    inputs: list[str] = Field(default_factory=list)
    outputs: list[str] = Field(default_factory=list)
    hard_gates: list[str] = Field(default_factory=list)

    model_config = {"json_schema_extra": {"title": "DevinClaw Skill Descriptor"}}


class KnowledgeEntrySchema(BaseModel):
    """Canonical KnowledgeEntry schema — a unit of learned context."""

    entry_id: str = Field(description="UUID v4 identifier")
    scope: str = Field(description="One of: session, user, org, project")
    scope_id: str = Field(description="ID of the scoped entity")
    key: str = Field(description="Short identifier / topic")
    value: str = Field(description="The knowledge content")
    source_session_id: str = Field(default="")
    created_at: datetime = Field(description="ISO-8601 creation timestamp")
    tags: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)

    model_config = {"json_schema_extra": {"title": "DevinClaw Knowledge Entry"}}


class EvidencePackSchema(BaseModel):
    """Canonical EvidencePack schema — tamper-evident compliance artifact."""

    session_id: str = Field(description="Primary Devin session ID")
    timestamp: datetime = Field(description="ISO-8601 generation timestamp")
    skill_id: str = Field(default="")
    work_order_id: str = Field(default="", description="Parent task ID")
    artifacts: list[dict[str, str]] = Field(default_factory=list, description="SHA-256 hashed file references")
    verification: dict[str, Any] = Field(
        default_factory=dict,
        description="SDLC gate results: gates_run, gates_passed, gates_failed",
    )
    knowledge_updates: list[dict[str, str]] = Field(default_factory=list)
    escalations: list[dict[str, Any]] = Field(default_factory=list)
    arena: dict[str, Any] | None = Field(
        default=None,
        description="Arena divergence result if arena-run mode was used",
    )
    stig_findings: list[dict[str, Any]] = Field(
        default_factory=list,
        description="STIG V-number findings with CAT severity",
    )
    nist_controls: list[str] = Field(
        default_factory=list,
        description="NIST 800-53 control IDs validated",
    )
    cve_scan: dict[str, Any] | None = Field(
        default=None,
        description="CVE scan summary (critical, high, medium, low counts)",
    )
    sha256_hash: str = Field(default="", description="SHA-256 of serialised pack for tamper evidence")
    retention_policy: str = Field(
        default="FAR 4.703 — contract duration + 3 years",
        description="Federal records retention requirement",
    )

    model_config = {"json_schema_extra": {"title": "DevinClaw Evidence Pack"}}


class EventSchema(BaseModel):
    """Canonical Event schema — a single audit trail entry."""

    event_id: str = Field(description="UUID v4 identifier")
    timestamp: datetime = Field(description="ISO-8601 event timestamp")
    event_type: str = Field(
        description="Event category: task_start | task_complete | task_failed | violation | session_start | escalation"
    )
    session_id: str = Field(default="")
    user_id: str = Field(default="")
    org_id: str = Field(default="")
    task_description: str = Field(default="")
    skill_used: str = Field(default="")
    spoke_used: str = Field(default="")
    artifacts: dict[str, str] = Field(default_factory=dict)
    sdlc_checklist: dict[str, bool] = Field(default_factory=dict)
    violations: list[dict[str, Any]] = Field(default_factory=list)
    duration_seconds: float = Field(default=0.0)
    outcome: str = Field(default="", description="success | failure | partial | blocked | escalated")
    notes: str = Field(default="")
    correlation_id: str = Field(default="", description="Links related events across the pipeline")
    ip_address: str = Field(default="")
    sha256_hash: str = Field(default="", description="Tamper-evidence hash")

    model_config = {"json_schema_extra": {"title": "DevinClaw Audit Event"}}


# ---------------------------------------------------------------------------
# Schema Registry — export all schemas + JSON Schema generation
# ---------------------------------------------------------------------------

SCHEMA_REGISTRY: dict[str, type[BaseModel]] = {
    "Task": TaskSchema,
    "Skill": SkillSchema,
    "KnowledgeEntry": KnowledgeEntrySchema,
    "EvidencePack": EvidencePackSchema,
    "Event": EventSchema,
}


def export_json_schemas() -> dict[str, dict[str, Any]]:
    """Export JSON Schema (Draft 2020-12) for every registered model.

    Returns a dict mapping model name to its JSON Schema.
    Useful for OpenAPI docs, compliance validation, and artifact schema checks.
    """
    return {name: model.model_json_schema() for name, model in SCHEMA_REGISTRY.items()}


def get_schema(name: str) -> dict[str, Any] | None:
    """Get the JSON Schema for a named model."""
    model = SCHEMA_REGISTRY.get(name)
    if model is None:
        return None
    return model.model_json_schema()
