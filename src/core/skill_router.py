"""Skill Router — matches natural language input to the appropriate skill.

Implements the routing algorithm from SKILLS-MAP.md lines 186-199:
  1. Extract keywords from user input (tokenization + stemming)
  2. Score each skill by trigger pattern match count
  3. SINGLE match  -> return that skill
  4. MULTIPLE      -> use priority order
  5. NO match      -> return skill-creator meta-skill
"""

from __future__ import annotations

import json
import logging
import os
import re
from dataclasses import dataclass, field

logger = logging.getLogger("devinclaw.skill_router")

# Priority order when multiple skills match (SKILLS-MAP.md lines 201-209)
PRIORITY_ORDER: list[str] = [
    "security-scan",
    "incident-response",
    "plsql-migration",
    "cobol-conversion",
    "db-rationalization",
    "api-modernization",
    "containerization",
    "parallel-migration",
    "legacy-analysis",
    "feature-dev",
    "test-generation",
    "pr-review",
    "sdlc-validator",
    "guardrail-auditor",
]

# Minimum confidence threshold — below this, the match is flagged as low-confidence
MINIMUM_CONFIDENCE_THRESHOLD: float = 0.3

# Simple stemming suffixes
_STEM_SUFFIXES = ("ing", "tion", "ment", "ness", "ize", "ise", "ed", "ly", "er", "es", "s")


@dataclass
class SkillDescriptor:
    """Machine-consumable skill metadata."""

    skill_id: str
    name: str
    path: str
    description: str
    triggers: list[str]
    sdlc_phase: str
    risk_level: str
    default_arena_mode: str
    arena_sessions: int
    mcp_required: list[str]
    spokes: list[str]
    inputs: list[str]
    outputs: list[str]
    hard_gates: list[str]


@dataclass
class SkillMatch:
    """Result of skill routing."""

    skill: SkillDescriptor
    score: float
    matched_triggers: list[str] = field(default_factory=list)
    is_fallback: bool = False
    low_confidence: bool = False


def _stem(word: str) -> str:
    """Naive suffix-stripping stemmer for trigger matching."""
    w = word.lower().strip()
    for suffix in _STEM_SUFFIXES:
        if len(w) > len(suffix) + 2 and w.endswith(suffix):
            return w[: -len(suffix)]
    return w


def _tokenize(text: str) -> list[str]:
    """Split text into lowercase tokens, removing punctuation."""
    tokens = re.findall(r"[a-z0-9/]+", text.lower())
    return tokens


class SkillRouter:
    """Routes natural language tasks to skills using trigger-based matching."""

    def __init__(self, skills_dir: str = "skills", audit_dir: str = "audit") -> None:
        self.skills_dir = skills_dir
        self.audit_dir = audit_dir
        self.skills: list[SkillDescriptor] = []
        self._fallback: SkillDescriptor | None = None

    def load(self) -> None:
        """Load skill descriptors from audit/skill-descriptors.json."""
        descriptors_path = os.path.join(self.audit_dir, "skill-descriptors.json")
        if not os.path.exists(descriptors_path):
            logger.warning("skill-descriptors.json not found at %s", descriptors_path)
            return

        with open(descriptors_path) as f:
            data = json.load(f)

        self.skills = []
        for entry in data.get("skills", []):
            sd = SkillDescriptor(
                skill_id=entry["skill_id"],
                name=entry["name"],
                path=entry.get("path", ""),
                description=entry.get("description", ""),
                triggers=entry.get("triggers", []),
                sdlc_phase=entry.get("sdlc_phase", ""),
                risk_level=entry.get("risk_level", "medium"),
                default_arena_mode=entry.get("default_arena_mode", "single-run"),
                arena_sessions=entry.get("arena_sessions", 1),
                mcp_required=entry.get("mcp_required", []),
                spokes=entry.get("spokes", []),
                inputs=entry.get("inputs", []),
                outputs=entry.get("outputs", []),
                hard_gates=entry.get("hard_gates", []),
            )
            if "_no_match_fallback" in sd.triggers:
                self._fallback = sd
            self.skills.append(sd)

        logger.info("Loaded %d skill descriptors", len(self.skills))

    def route_task(self, user_input: str) -> SkillMatch:
        """Route a natural language task to the best-matching skill.

        Algorithm:
          1. Tokenize + stem user input
          2. For each skill, count how many trigger phrases match
          3. Single match  -> return it
          4. Multiple      -> pick by priority order
          5. No match      -> skill-creator fallback
        """
        tokens = _tokenize(user_input)
        stemmed_tokens = [_stem(t) for t in tokens]
        input_text = user_input.lower()

        scored: list[tuple[SkillDescriptor, float, list[str]]] = []

        for skill in self.skills:
            if "_no_match_fallback" in skill.triggers:
                continue

            matched_triggers: list[str] = []
            score = 0.0

            for trigger in skill.triggers:
                trigger_lower = trigger.lower()

                # Exact phrase match (highest weight)
                if trigger_lower in input_text:
                    matched_triggers.append(trigger)
                    score += 2.0
                    continue

                # Token-level match
                trigger_tokens = _tokenize(trigger_lower)
                trigger_stems = [_stem(t) for t in trigger_tokens]
                overlap = sum(1 for ts in trigger_stems if ts in stemmed_tokens)
                if overlap > 0 and overlap >= len(trigger_stems) * 0.5:
                    matched_triggers.append(trigger)
                    score += overlap / len(trigger_stems)

            if score > 0:
                scored.append((skill, score, matched_triggers))

        if not scored:
            # Fallback to skill-creator
            if self._fallback:
                return SkillMatch(skill=self._fallback, score=0.0, is_fallback=True)
            msg = "No skill match and no fallback skill-creator registered"
            raise ValueError(msg)

        # Sort by score descending
        scored.sort(key=lambda x: x[1], reverse=True)

        if len(scored) == 1:
            skill, score, triggers = scored[0]
            return SkillMatch(
                skill=skill,
                score=score,
                matched_triggers=triggers,
                low_confidence=score < MINIMUM_CONFIDENCE_THRESHOLD,
            )

        # Multiple matches — use priority order
        top_score = scored[0][1]
        candidates = [(s, sc, t) for s, sc, t in scored if sc >= top_score * 0.7]

        for priority_name in PRIORITY_ORDER:
            for skill, score, triggers in candidates:
                if skill.name == priority_name:
                    return SkillMatch(
                        skill=skill,
                        score=score,
                        matched_triggers=triggers,
                        low_confidence=score < MINIMUM_CONFIDENCE_THRESHOLD,
                    )

        # If none in priority list, return highest score
        skill, score, triggers = scored[0]
        return SkillMatch(
            skill=skill,
            score=score,
            matched_triggers=triggers,
            low_confidence=score < MINIMUM_CONFIDENCE_THRESHOLD,
        )

    def get_skill_by_name(self, name: str) -> SkillDescriptor | None:
        """Look up a skill by name."""
        for skill in self.skills:
            if skill.name == name:
                return skill
        return None

    def list_skills(self) -> list[SkillDescriptor]:
        """Return all registered skills."""
        return list(self.skills)
