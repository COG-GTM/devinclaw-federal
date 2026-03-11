"""Orchestrator — the main orchestration loop tying all components together.

Steps:
  1. Receive task
  2. Authenticate + authorize (RBAC)
  3. Route to skill (skill_router)
  4. Check guardrails (guardrail_enforcer)
  5. Select spoke (spoke_selector)
  6. Determine arena mode (arena_executor)
  7. Launch session(s) (session_manager)
  8. Monitor + collect artifacts
  9. Validate SDLC gates (sdlc_validator)
  10. Write audit trail (audit_writer)
  11. Update memory (memory_manager)
  12. Notify user
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from src.core.arena_executor import ArenaExecutor
from src.core.audit_writer import AuditEntry, AuditWriter, EvidencePack
from src.core.guardrail_enforcer import GuardrailAction, GuardrailEnforcer
from src.core.guardrail_enforcer import TaskContext as GuardrailContext
from src.core.sdlc_validator import SDLCContext, SDLCValidator
from src.core.session_manager import SessionManager, SessionStatus
from src.core.skill_router import SkillRouter
from src.core.spoke_selector import SpokeSelection, select_spoke
from src.core.spoke_selector import TaskContext as SpokeContext
from src.memory.memory_manager import MemoryManager

logger = logging.getLogger("devinclaw.orchestrator")


@dataclass
class TaskRequest:
    """Incoming task request."""

    description: str
    user_id: str
    org_id: str
    repos: list[str] = field(default_factory=list)
    secrets: dict[str, str] = field(default_factory=dict)
    override_skill: str | None = None
    override_arena_mode: str | None = None
    is_safety_critical: bool = False
    batch_size: int = 1
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskResult:
    """Orchestration result for a completed task."""

    task_id: str
    status: str  # completed | failed | escalated | blocked
    skill_name: str = ""
    spoke: str = ""
    arena_mode: str = "single-run"
    session_ids: list[str] = field(default_factory=list)
    guardrail_results: list[dict[str, Any]] = field(default_factory=list)
    sdlc_result: dict[str, Any] = field(default_factory=dict)
    artifacts: list[dict[str, Any]] = field(default_factory=list)
    evidence_pack_path: str = ""
    errors: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    duration_seconds: float = 0.0


class Orchestrator:
    """Main orchestration engine for DevinClaw Federal."""

    def __init__(
        self,
        skill_router: SkillRouter,
        guardrail_enforcer: GuardrailEnforcer,
        sdlc_validator: SDLCValidator,
        arena_executor: ArenaExecutor,
        session_manager: SessionManager,
        audit_writer: AuditWriter,
        memory_manager: MemoryManager,
    ) -> None:
        self.skill_router = skill_router
        self.guardrail_enforcer = guardrail_enforcer
        self.sdlc_validator = sdlc_validator
        self.arena_executor = arena_executor
        self.session_manager = session_manager
        self.audit_writer = audit_writer
        self.memory_manager = memory_manager

    async def execute_task(self, request: TaskRequest) -> TaskResult:
        """Execute the full orchestration pipeline for a task."""
        task_id = str(uuid4())
        start_time = datetime.now(UTC)
        result = TaskResult(task_id=task_id, status="running")

        try:
            # Step 1: Write audit entry for task start
            self.audit_writer.write_entry(
                AuditEntry(
                    event_type="task_start",
                    session_id="",
                    user_id=request.user_id,
                    org_id=request.org_id,
                    task_description=request.description,
                    correlation_id=task_id,
                )
            )

            # Step 2: Route to skill
            if request.override_skill:
                skill = self.skill_router.get_skill_by_name(request.override_skill)
                if not skill:
                    result.status = "failed"
                    result.errors.append(f"Skill not found: {request.override_skill}")
                    return result
            else:
                match = self.skill_router.route_task(request.description)
                skill = match.skill
                logger.info("Routed task %s to skill %s (score=%.2f)", task_id, skill.name, match.score)

            result.skill_name = skill.name

            # Step 3: Check guardrails (pre-execution)
            guardrail_ctx = GuardrailContext(
                target_repos=request.repos,
                metadata=request.metadata,
            )
            guardrail_results = self.guardrail_enforcer.evaluate_guardrails(guardrail_ctx)
            result.guardrail_results = [
                {
                    "rule_id": gr.rule_id,
                    "name": gr.name,
                    "passed": gr.passed,
                    "severity": gr.severity.value,
                    "action": gr.action.value,
                    "details": gr.details,
                }
                for gr in guardrail_results
            ]

            # Check for blocking guardrails
            for gr in guardrail_results:
                if not gr.passed and gr.action in (GuardrailAction.BLOCK_SESSION, GuardrailAction.BLOCK_MERGE):
                    result.status = "blocked"
                    result.errors.append(f"Guardrail {gr.rule_id} ({gr.name}) blocked: {gr.details}")
                    self.audit_writer.write_entry(
                        AuditEntry(
                            event_type="violation",
                            user_id=request.user_id,
                            org_id=request.org_id,
                            task_description=request.description,
                            skill_used=skill.name,
                            violations=[{"rule": gr.rule_id, "details": gr.details}],
                            outcome="blocked",
                            correlation_id=task_id,
                        )
                    )
                    return result

            # Step 4: Select spoke
            spoke_ctx = SpokeContext(
                batch_size=request.batch_size,
                network_available=True,
            )
            spoke_selection: SpokeSelection = select_spoke(skill.name, spoke_ctx)
            result.spoke = spoke_selection.primary.value
            logger.info("Selected spoke: %s (fallback: %s)", spoke_selection.primary, spoke_selection.fallback)

            # Step 5: Determine arena mode
            mode, session_count = self.arena_executor.determine_execution_mode(
                skill_name=skill.name,
                is_safety_critical=request.is_safety_critical,
                override_mode=request.override_arena_mode,
            )
            result.arena_mode = mode

            # Step 6: Inject relevant memories
            memories = self.memory_manager.search(
                query=request.description,
                scope="org",
                scope_id=request.org_id,
                limit=5,
            )
            context_prefix = ""
            if memories:
                context_lines = ["## Relevant Knowledge from Previous Sessions"]
                for mem in memories:
                    context_lines.append(f"- {mem.value}")
                context_prefix = "\n".join(context_lines) + "\n\n"

            prompt = context_prefix + request.description

            # Step 7: Launch session(s)
            session_ids: list[str] = []
            for _ in range(session_count):
                record = await self.session_manager.launch_session(
                    task_id=task_id,
                    user_id=request.user_id,
                    org_id=request.org_id,
                    prompt=prompt,
                    skill_name=skill.name,
                    spoke=spoke_selection.primary.value,
                    repos=request.repos,
                    secrets=request.secrets,
                )
                session_ids.append(record.session_id)

            result.session_ids = session_ids

            # Step 8: Monitor sessions (poll until complete)
            completed_records = []
            for sid in session_ids:
                record = await self.session_manager.poll_until_complete(sid)
                completed_records.append(record)

            # Step 9: Arena divergence check (if arena mode)
            if mode == "arena-run" and len(completed_records) > 1:
                outputs = [{"findings": r.artifacts, "metadata": r.metadata} for r in completed_records]
                divergence = self.arena_executor.compute_divergence(outputs)
                if divergence.resolution == "human-escalated":
                    result.status = "escalated"
                    logger.warning("Arena divergence %.2f exceeds threshold — escalating", divergence.score)

            # Collect artifacts from all sessions
            for record in completed_records:
                result.artifacts.extend(record.artifacts)

            # Step 10: SDLC validation
            any_failed = any(r.status == SessionStatus.FAILED for r in completed_records)
            sdlc_ctx = SDLCContext(
                tests_passing=not any_failed,
                metadata={"task_id": task_id, "session_ids": session_ids},
            )
            sdlc_result = self.sdlc_validator.validate(sdlc_ctx)
            result.sdlc_result = sdlc_result.to_dict()

            # Step 11: Write evidence pack
            pack = EvidencePack(
                session_id=session_ids[0] if session_ids else task_id,
                skill_id=skill.skill_id,
                work_order_id=task_id,
                verification={
                    "gates_run": [c.check_id for c in sdlc_result.checks],
                    "gates_passed": [c.check_id for c in sdlc_result.checks if c.passed],
                    "gates_failed": [c.check_id for c in sdlc_result.checks if c.passed is False],
                },
            )
            result.evidence_pack_path = self.audit_writer.write_evidence_pack(pack)

            # Step 12: Update memory
            if result.status != "failed":
                self.memory_manager.store(
                    scope="session",
                    scope_id=task_id,
                    key=f"task-{task_id}-outcome",
                    value=f"Skill {skill.name} completed for: {request.description[:100]}",
                    source_session_id=session_ids[0] if session_ids else "",
                    tags=[skill.name, result.status],
                )

            # Final status
            if result.status == "running":
                result.status = "completed" if not any_failed else "failed"

            elapsed = (datetime.now(UTC) - start_time).total_seconds()
            result.duration_seconds = elapsed

            # Final audit entry
            self.audit_writer.write_entry(
                AuditEntry(
                    event_type="task_complete" if result.status == "completed" else "task_failed",
                    session_id=session_ids[0] if session_ids else "",
                    user_id=request.user_id,
                    org_id=request.org_id,
                    task_description=request.description,
                    skill_used=skill.name,
                    spoke_used=spoke_selection.primary.value,
                    outcome=result.status,
                    duration_seconds=elapsed,
                    correlation_id=task_id,
                )
            )

        except Exception as e:
            logger.exception("Task %s failed with error", task_id)
            result.status = "failed"
            result.errors.append(str(e))
            self.audit_writer.write_entry(
                AuditEntry(
                    event_type="task_failed",
                    user_id=request.user_id,
                    org_id=request.org_id,
                    task_description=request.description,
                    outcome="failure",
                    notes=str(e),
                    correlation_id=task_id,
                )
            )

        return result
