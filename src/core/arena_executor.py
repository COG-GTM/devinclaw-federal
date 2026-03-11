"""Arena Executor — risk-based multi-session verification.

Implements the arena pattern from docs/VERIFICATION-SYSTEM.md:
  - Determine execution mode (single-run vs arena-run) based on skill risk level
  - Launch N parallel sessions
  - Compute divergence score
  - Auto-merge or escalate to human
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from typing import Any

from src.config import settings

logger = logging.getLogger("devinclaw.arena_executor")


@dataclass
class ArenaConfig:
    """Per-skill arena configuration."""

    skill_name: str
    risk_level: str
    default_mode: str
    arena_sessions: int
    rationale: str
    override_requires_justification: bool = False
    override_minimum_mode: str | None = None


@dataclass
class DivergenceResult:
    """Result of divergence computation across arena sessions."""

    score: float
    entity_overlap_ratio: float
    invariant_agreement_ratio: float
    conflicting_claims_ratio: float
    confidence_alignment_ratio: float
    resolution: str  # auto-merged | targeted-verification | human-escalated


@dataclass
class ArenaResult:
    """Result of arena execution."""

    mode: str  # single-run | arena-run
    session_count: int
    session_ids: list[str] = field(default_factory=list)
    divergence: DivergenceResult | None = None
    merged_artifacts: list[dict[str, Any]] = field(default_factory=list)
    escalation_required: bool = False
    confidence_score: float = 0.0


class ArenaExecutor:
    """Manages arena-pattern execution for risk-based verification."""

    def __init__(self, audit_dir: str = "audit") -> None:
        self.audit_dir = audit_dir
        self.configs: dict[str, ArenaConfig] = {}
        self.divergence_threshold = settings.divergence_threshold
        self.safety_critical_override: dict[str, Any] = {}

    def load(self) -> None:
        """Load arena configuration from audit/arena-config.json."""
        config_path = os.path.join(self.audit_dir, "arena-config.json")
        if not os.path.exists(config_path):
            logger.warning("arena-config.json not found at %s", config_path)
            return

        with open(config_path) as f:
            data = json.load(f)

        self.divergence_threshold = data.get("divergence_threshold", 0.35)
        self.safety_critical_override = data.get("safety_critical_override", {})

        for skill_name, cfg in data.get("skills", {}).items():
            self.configs[skill_name] = ArenaConfig(
                skill_name=skill_name,
                risk_level=cfg.get("risk_level", "medium"),
                default_mode=cfg.get("default_mode", "single-run"),
                arena_sessions=cfg.get("arena_sessions", 1),
                rationale=cfg.get("rationale", ""),
                override_requires_justification=cfg.get("override_requires_justification", False),
                override_minimum_mode=cfg.get("override_minimum_mode"),
            )
        logger.info("Loaded arena configs for %d skills", len(self.configs))

    def determine_execution_mode(
        self,
        skill_name: str,
        is_safety_critical: bool = False,
        override_mode: str | None = None,
    ) -> tuple[str, int]:
        """Determine whether a task runs as single-run or arena-run.

        Returns:
            (mode, session_count)
        """
        # Safety-critical override (DO-178C DAL A-C)
        if is_safety_critical:
            forced_sessions = self.safety_critical_override.get("forced_sessions", 3)
            return "arena-run", forced_sessions

        config = self.configs.get(skill_name)
        if not config:
            return "single-run", 1

        # Check user override
        if override_mode:
            if override_mode == "single-run" and config.override_minimum_mode == "arena-run":
                logger.warning(
                    "Cannot override %s to single-run — minimum mode is arena-run",
                    skill_name,
                )
                return config.default_mode, config.arena_sessions
            if override_mode == "single-run":
                return "single-run", 1
            if override_mode == "arena-run":
                return "arena-run", max(config.arena_sessions, 2)

        return config.default_mode, config.arena_sessions

    def compute_divergence(
        self,
        session_outputs: list[dict[str, Any]],
    ) -> DivergenceResult:
        """Compute divergence across arena session outputs.

        Formula from VERIFICATION-SYSTEM.md lines 37-44:
          divergence = 1.0 - (
            0.30 * entity_overlap_ratio +
            0.30 * invariant_agreement_ratio +
            0.25 * (1.0 - conflicting_claims_ratio) +
            0.15 * confidence_alignment_ratio
          )
        """
        if len(session_outputs) < 2:
            return DivergenceResult(
                score=0.0,
                entity_overlap_ratio=1.0,
                invariant_agreement_ratio=1.0,
                conflicting_claims_ratio=0.0,
                confidence_alignment_ratio=1.0,
                resolution="auto-merged",
            )

        # Extract entities from each session
        all_entity_sets: list[set[str]] = []
        all_severities: list[dict[str, str]] = []

        for output in session_outputs:
            entities: set[str] = set()
            severities: dict[str, str] = {}
            for finding in output.get("findings", []):
                entity_key = finding.get("entity", finding.get("file", "unknown"))
                entities.add(entity_key)
                severities[entity_key] = finding.get("severity", "unknown")
            all_entity_sets.append(entities)
            all_severities.append(severities)

        # Entity overlap: Jaccard similarity across all sessions
        if all_entity_sets:
            union = set().union(*all_entity_sets)
            intersection = set(all_entity_sets[0])
            for es in all_entity_sets[1:]:
                intersection &= es
            entity_overlap = len(intersection) / len(union) if union else 1.0
        else:
            entity_overlap = 1.0

        # Invariant agreement: check if key findings are consistent
        invariant_agreement = self._compute_invariant_agreement(session_outputs)

        # Conflicting claims
        conflicting_claims = self._compute_conflicting_claims(all_entity_sets, all_severities)

        # Confidence alignment
        confidence_alignment = self._compute_confidence_alignment(session_outputs)

        # Divergence formula
        score = 1.0 - (
            0.30 * entity_overlap
            + 0.30 * invariant_agreement
            + 0.25 * (1.0 - conflicting_claims)
            + 0.15 * confidence_alignment
        )
        score = max(0.0, min(1.0, score))

        # Determine resolution
        if score < 0.15:
            resolution = "auto-merged"
        elif score < self.divergence_threshold:
            resolution = "auto-merged"  # with annotations
        else:
            resolution = "human-escalated"

        return DivergenceResult(
            score=score,
            entity_overlap_ratio=entity_overlap,
            invariant_agreement_ratio=invariant_agreement,
            conflicting_claims_ratio=conflicting_claims,
            confidence_alignment_ratio=confidence_alignment,
            resolution=resolution,
        )

    def compute_confidence_score(
        self,
        base_confidence: float,
        arena_confirmed: bool = False,
        review_confirmed: bool = False,
        test_evidence: bool = False,
        stig_match: bool = False,
        arena_contradicted: bool = False,
        incomplete_indexing: bool = False,
        known_limitations: bool = False,
        pattern_only: bool = False,
    ) -> float:
        """Compute confidence score with boosters and reducers.

        From VERIFICATION-SYSTEM.md lines 98-108.
        """
        score = base_confidence

        # Boosters
        if arena_confirmed:
            score += 0.15
        if review_confirmed:
            score += 0.10
        if test_evidence:
            score += 0.10
        if stig_match:
            score += 0.10

        # Reducers
        if arena_contradicted:
            score -= 0.20
        if incomplete_indexing:
            score -= 0.15
        if known_limitations:
            score -= 0.10
        if pattern_only:
            score -= 0.10

        return max(0.0, min(1.0, score))

    def _compute_invariant_agreement(self, session_outputs: list[dict[str, Any]]) -> float:
        """Check agreement on top-level patterns across sessions."""
        if len(session_outputs) < 2:
            return 1.0

        # Compare summary keys across sessions
        summaries: list[set[str]] = []
        for output in session_outputs:
            summary_keys = set()
            for key in ("architecture", "primary_risk", "tech_stack", "recommendation"):
                val = output.get(key, "")
                if val:
                    summary_keys.add(f"{key}:{val}")
            summaries.append(summary_keys)

        if not any(summaries):
            return 1.0

        # Agreement = average pairwise overlap
        pairs = 0
        total_overlap = 0.0
        for i in range(len(summaries)):
            for j in range(i + 1, len(summaries)):
                pairs += 1
                union = summaries[i] | summaries[j]
                intersection = summaries[i] & summaries[j]
                total_overlap += len(intersection) / len(union) if union else 1.0

        return total_overlap / pairs if pairs else 1.0

    def _compute_conflicting_claims(
        self,
        entity_sets: list[set[str]],
        severities: list[dict[str, str]],
    ) -> float:
        """Detect severity disagreements on shared entities."""
        if len(entity_sets) < 2:
            return 0.0

        # Find entities in multiple sessions
        all_entities = set().union(*entity_sets)
        conflicts = 0
        shared = 0

        for entity in all_entities:
            present_in = [i for i, es in enumerate(entity_sets) if entity in es]
            if len(present_in) > 1:
                shared += 1
                sev_values = {severities[i].get(entity, "unknown") for i in present_in}
                if len(sev_values) > 1:
                    conflicts += 1

        return conflicts / shared if shared else 0.0

    def _compute_confidence_alignment(self, session_outputs: list[dict[str, Any]]) -> float:
        """Check alignment of confidence scores across sessions."""
        confidence_lists: list[list[float]] = []
        for output in session_outputs:
            confidences: list[float] = []
            for finding in output.get("findings", []):
                conf = finding.get("confidence", 0.5)
                confidences.append(conf)
            confidence_lists.append(confidences)

        if not confidence_lists or not any(confidence_lists):
            return 1.0

        # Average confidence per session
        avgs = [sum(cl) / len(cl) if cl else 0.5 for cl in confidence_lists]
        if len(avgs) < 2:
            return 1.0

        # Alignment = 1 - normalized spread
        spread = max(avgs) - min(avgs)
        return max(0.0, 1.0 - spread)
