"""SDLC Validator — validates task completion against the full 10-item SDLC checklist.

Extends scripts/validate_sdlc.py to cover all 10 items from audit/sdlc-checklist.json:
  SDLC-001: Spec exists
  SDLC-002: Tests exist
  SDLC-003: Tests pass
  SDLC-004: Coverage meets minimum thresholds
  SDLC-005: Devin Review completed
  SDLC-006: No unresolved CRITICAL bugs
  SDLC-007: Security scan completed
  SDLC-008: Guardrails zero CRITICAL/HIGH
  SDLC-009: Knowledge base updated
  SDLC-010: PR description complete
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger("devinclaw.sdlc_validator")


@dataclass
class SDLCCheckResult:
    """Result of a single SDLC check."""

    check_id: str
    phase: str
    requirement: str
    passed: bool | None  # None = skipped
    detail: str
    required: bool = True


@dataclass
class SDLCValidationResult:
    """Aggregate result of SDLC validation."""

    checks: list[SDLCCheckResult]
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    verdict: str = "UNKNOWN"

    def compute_verdict(self) -> None:
        self.passed = sum(1 for c in self.checks if c.passed is True)
        self.failed = sum(1 for c in self.checks if c.passed is False and c.required)
        self.skipped = sum(1 for c in self.checks if c.passed is None)
        self.verdict = "PASS" if self.failed == 0 else "FAIL"

    def to_dict(self) -> dict[str, Any]:
        return {
            "checks": [
                {
                    "id": c.check_id,
                    "phase": c.phase,
                    "requirement": c.requirement,
                    "passed": c.passed,
                    "detail": c.detail,
                    "required": c.required,
                }
                for c in self.checks
            ],
            "passed": self.passed,
            "failed": self.failed,
            "skipped": self.skipped,
            "verdict": self.verdict,
        }


@dataclass
class SDLCContext:
    """Context for SDLC validation."""

    spec_exists: bool = False
    tests_exist: bool = False
    tests_passing: bool = False
    coverage_branch_percent: float = 0.0
    coverage_line_percent: float = 0.0
    coverage_threshold: float = 80.0
    review_complete: bool = False
    critical_bugs_count: int = 0
    security_scan_complete: bool = False
    security_scan_cat1_findings: int = 0
    guardrail_critical_count: int = 0
    guardrail_high_count: int = 0
    knowledge_updated: bool = False
    pr_description: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)


class SDLCValidator:
    """Validates task completion against the full SDLC checklist."""

    def __init__(self, audit_dir: str = "audit") -> None:
        self.audit_dir = audit_dir
        self.checklist: list[dict[str, Any]] = []

    def load(self) -> None:
        """Load the SDLC checklist from audit/sdlc-checklist.json."""
        checklist_path = os.path.join(self.audit_dir, "sdlc-checklist.json")
        if not os.path.exists(checklist_path):
            logger.warning("sdlc-checklist.json not found at %s", checklist_path)
            return

        with open(checklist_path) as f:
            data = json.load(f)
        self.checklist = data.get("checklist", [])
        logger.info("Loaded %d SDLC checklist items", len(self.checklist))

    def validate(self, context: SDLCContext) -> SDLCValidationResult:
        """Run all SDLC checks against the provided context."""
        checks = [
            self._check_sdlc_001(context),
            self._check_sdlc_002(context),
            self._check_sdlc_003(context),
            self._check_sdlc_004(context),
            self._check_sdlc_005(context),
            self._check_sdlc_006(context),
            self._check_sdlc_007(context),
            self._check_sdlc_008(context),
            self._check_sdlc_009(context),
            self._check_sdlc_010(context),
        ]

        result = SDLCValidationResult(checks=checks)
        result.compute_verdict()
        return result

    def _check_sdlc_001(self, ctx: SDLCContext) -> SDLCCheckResult:
        """SDLC-001: SDD spec document exists."""
        return SDLCCheckResult(
            check_id="SDLC-001",
            phase="specification",
            requirement="SDD spec document exists",
            passed=ctx.spec_exists,
            detail="Spec found" if ctx.spec_exists else "No spec file found",
        )

    def _check_sdlc_002(self, ctx: SDLCContext) -> SDLCCheckResult:
        """SDLC-002: TDD test plan exists."""
        return SDLCCheckResult(
            check_id="SDLC-002",
            phase="testing",
            requirement="TDD test plan exists",
            passed=ctx.tests_exist,
            detail="Test files found" if ctx.tests_exist else "No test files found",
        )

    def _check_sdlc_003(self, ctx: SDLCContext) -> SDLCCheckResult:
        """SDLC-003: All tests passing."""
        return SDLCCheckResult(
            check_id="SDLC-003",
            phase="testing",
            requirement="All tests passing",
            passed=ctx.tests_passing,
            detail="Tests passing" if ctx.tests_passing else "Tests failing or not run",
        )

    def _check_sdlc_004(self, ctx: SDLCContext) -> SDLCCheckResult:
        """SDLC-004: Coverage meets minimum thresholds."""
        passed = ctx.coverage_branch_percent >= ctx.coverage_threshold
        return SDLCCheckResult(
            check_id="SDLC-004",
            phase="testing",
            requirement="Coverage meets minimum thresholds",
            passed=passed,
            detail=f"Branch coverage: {ctx.coverage_branch_percent:.1f}% (threshold: {ctx.coverage_threshold}%)",
        )

    def _check_sdlc_005(self, ctx: SDLCContext) -> SDLCCheckResult:
        """SDLC-005: Devin Review completed."""
        return SDLCCheckResult(
            check_id="SDLC-005",
            phase="review",
            requirement="Devin Review completed",
            passed=ctx.review_complete,
            detail="Review complete" if ctx.review_complete else "Review not completed",
        )

    def _check_sdlc_006(self, ctx: SDLCContext) -> SDLCCheckResult:
        """SDLC-006: No unresolved CRITICAL bugs."""
        passed = ctx.critical_bugs_count == 0
        return SDLCCheckResult(
            check_id="SDLC-006",
            phase="review",
            requirement="No unresolved CRITICAL bugs from Devin Review",
            passed=passed,
            detail=f"{ctx.critical_bugs_count} critical bug(s)" if not passed else "Zero critical bugs",
        )

    def _check_sdlc_007(self, ctx: SDLCContext) -> SDLCCheckResult:
        """SDLC-007: Security scan completed with zero CAT I findings."""
        if not ctx.security_scan_complete:
            return SDLCCheckResult(
                check_id="SDLC-007",
                phase="security",
                requirement="Security scan completed",
                passed=False,
                detail="Security scan not completed",
            )
        passed = ctx.security_scan_cat1_findings == 0
        return SDLCCheckResult(
            check_id="SDLC-007",
            phase="security",
            requirement="Security scan completed",
            passed=passed,
            detail=(
                f"CAT I findings: {ctx.security_scan_cat1_findings}" if not passed else "Security scan clean — 0 CAT I"
            ),
        )

    def _check_sdlc_008(self, ctx: SDLCContext) -> SDLCCheckResult:
        """SDLC-008: Guardrails zero CRITICAL/HIGH violations."""
        total = ctx.guardrail_critical_count + ctx.guardrail_high_count
        passed = total == 0
        return SDLCCheckResult(
            check_id="SDLC-008",
            phase="governance",
            requirement="Guardrails: zero CRITICAL/HIGH violations",
            passed=passed,
            detail=(
                f"CRITICAL: {ctx.guardrail_critical_count}, HIGH: {ctx.guardrail_high_count}"
                if not passed
                else "Zero CRITICAL/HIGH violations"
            ),
        )

    def _check_sdlc_009(self, ctx: SDLCContext) -> SDLCCheckResult:
        """SDLC-009: Knowledge base updated (not required)."""
        return SDLCCheckResult(
            check_id="SDLC-009",
            phase="knowledge",
            requirement="Knowledge base updated",
            passed=ctx.knowledge_updated if ctx.knowledge_updated else None,
            detail="Knowledge updated" if ctx.knowledge_updated else "Knowledge not updated (optional)",
            required=False,
        )

    def _check_sdlc_010(self, ctx: SDLCContext) -> SDLCCheckResult:
        """SDLC-010: PR description complete."""
        has_desc = len(ctx.pr_description.strip()) > 20
        return SDLCCheckResult(
            check_id="SDLC-010",
            phase="documentation",
            requirement="PR description complete",
            passed=has_desc,
            detail="PR description present" if has_desc else "PR description missing or insufficient",
        )
