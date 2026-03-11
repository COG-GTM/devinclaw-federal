"""Spoke Selector — determines the Devin execution spoke for a task.

Implements the Spoke Selection Matrix from TOOLS.md lines 104-118.
"""

from __future__ import annotations

import logging
import os
import shutil
from dataclasses import dataclass
from enum import StrEnum

from src.config import settings

logger = logging.getLogger("devinclaw.spoke_selector")


class Spoke(StrEnum):
    """Devin execution spokes."""

    CLOUD = "devin-cloud"
    CLI = "devin-cli"
    API = "devin-api"
    REVIEW = "devin-review"
    IDE = "devin-ide"


@dataclass
class SpokeSelection:
    """Result of spoke selection."""

    primary: Spoke
    fallback: Spoke | None
    rationale: str


@dataclass
class TaskContext:
    """Context used for spoke selection decisions."""

    batch_size: int = 1
    network_available: bool = True
    classification_level: str = "unclassified"  # unclassified, cui, secret, top_secret
    is_pr_review: bool = False
    is_ci_cd: bool = False
    interactive: bool = False
    air_gapped: bool = False


def _cli_available() -> bool:
    """Check if Devin CLI is available locally."""
    return shutil.which(settings.devin_cli_path) is not None


def _api_key_configured() -> bool:
    """Check if Devin API key is configured."""
    return bool(settings.devin_api_key)


def _network_available() -> bool:
    """Basic network availability check."""
    return os.environ.get("DEVINCLAW_AIRGAP", "false").lower() != "true"


def select_spoke(skill_name: str, context: TaskContext) -> SpokeSelection:
    """Select the best spoke for a given skill and context.

    Uses the Spoke Selection Matrix from TOOLS.md.
    """
    # Air-gapped / classified environments -> CLI only
    if context.air_gapped or context.classification_level in ("secret", "top_secret"):
        return SpokeSelection(
            primary=Spoke.CLI,
            fallback=None,
            rationale=f"Air-gapped or classified ({context.classification_level}) environment — CLI only",
        )

    # PR review tasks -> Review spoke
    if context.is_pr_review or skill_name == "pr-review":
        return SpokeSelection(
            primary=Spoke.REVIEW,
            fallback=Spoke.API,
            rationale="PR compliance check — Review spoke is webhook-native",
        )

    # CI/CD pipeline tasks -> API spoke
    if context.is_ci_cd:
        return SpokeSelection(
            primary=Spoke.API,
            fallback=Spoke.CLOUD,
            rationale="CI/CD pipeline integration — API spoke",
        )

    # Interactive development -> CLI
    if context.interactive:
        fallback = Spoke.CLI if _cli_available() else None
        return SpokeSelection(
            primary=Spoke.CLI,
            fallback=fallback,
            rationale="Interactive development — developer-in-the-loop",
        )

    # Batch migration (100+ files) -> Cloud
    if context.batch_size > 10:
        return SpokeSelection(
            primary=Spoke.CLOUD,
            fallback=Spoke.API,
            rationale=f"Batch operation ({context.batch_size} items) — Cloud maximizes parallelism",
        )

    # Single file fix -> API (lightweight, fast)
    if context.batch_size == 1:
        if _api_key_configured():
            return SpokeSelection(
                primary=Spoke.API,
                fallback=Spoke.CLI if _cli_available() else None,
                rationale="Single task — API spoke is lightweight and fast",
            )
        if _cli_available():
            return SpokeSelection(
                primary=Spoke.CLI,
                fallback=None,
                rationale="Single task — CLI available, API key not configured",
            )

    # Default: Cloud with API fallback
    return SpokeSelection(
        primary=Spoke.CLOUD,
        fallback=Spoke.API if _api_key_configured() else (Spoke.CLI if _cli_available() else None),
        rationale="Default — Cloud spoke with API fallback",
    )
