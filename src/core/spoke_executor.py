"""Spoke Executor — common interface contract for all execution spokes.

Defines the abstract base class that every spoke implements, ensuring skills
are interchangeable across API/CLI/Cloud/Review/IDE.  The SpokeExecutorFactory
returns the correct concrete executor based on spoke enum value.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from src.config import settings
from src.core.spoke_selector import Spoke

logger = logging.getLogger("devinclaw.spoke_executor")


# ---------------------------------------------------------------------------
# Common data types shared across all spokes
# ---------------------------------------------------------------------------


@dataclass
class SpokeRequest:
    """Uniform request payload accepted by every spoke executor."""

    task_id: str
    prompt: str
    skill_name: str
    user_id: str
    org_id: str
    repos: list[str] = field(default_factory=list)
    secrets: dict[str, str] = field(default_factory=dict)
    playbook_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SpokeSession:
    """Uniform session handle returned by every spoke executor."""

    session_id: str
    spoke: Spoke
    status: str = "queued"  # queued | running | completed | failed | cancelled
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    messages: list[dict[str, Any]] = field(default_factory=list)
    artifacts: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Abstract Base Class — every spoke MUST implement these four methods
# ---------------------------------------------------------------------------


class SpokeExecutor(ABC):
    """Common interface contract for Devin execution spokes.

    Every spoke (Cloud, CLI, API, Review, IDE) implements:
      - execute()  — launch a session and return a handle
      - status()   — poll the current session state
      - cancel()   — request graceful cancellation
      - collect()  — gather artifacts after completion
    """

    spoke: Spoke

    @abstractmethod
    async def execute(self, request: SpokeRequest) -> SpokeSession:
        """Launch a new session on this spoke."""

    @abstractmethod
    async def status(self, session_id: str) -> str:
        """Return the current status string for *session_id*."""

    @abstractmethod
    async def cancel(self, session_id: str) -> bool:
        """Request cancellation.  Returns True if accepted."""

    @abstractmethod
    async def collect(self, session_id: str) -> list[dict[str, Any]]:
        """Collect artifacts produced by the session."""


# ---------------------------------------------------------------------------
# Concrete implementations
# ---------------------------------------------------------------------------


class CloudSpokeExecutor(SpokeExecutor):
    """Devin Cloud — parallel autonomous sessions via the Devin REST API."""

    spoke = Spoke.CLOUD

    async def execute(self, request: SpokeRequest) -> SpokeSession:
        import httpx

        async with httpx.AsyncClient(
            base_url=settings.devin_api_base_url.rstrip("/"),
            headers={"Authorization": f"Bearer {settings.devin_api_key}", "Content-Type": "application/json"},
            timeout=httpx.Timeout(30.0, connect=10.0),
        ) as client:
            payload: dict[str, Any] = {"prompt": request.prompt}
            if request.playbook_id:
                payload["playbook_id"] = request.playbook_id
            if request.repos:
                payload["repos"] = request.repos
            resp = await client.post("/sessions", json=payload)
            resp.raise_for_status()
            data = resp.json()

        session_id = data.get("session_id", data.get("id", "unknown"))
        return SpokeSession(session_id=session_id, spoke=self.spoke, status="queued")

    async def status(self, session_id: str) -> str:
        import httpx

        async with httpx.AsyncClient(
            base_url=settings.devin_api_base_url.rstrip("/"),
            headers={"Authorization": f"Bearer {settings.devin_api_key}"},
            timeout=httpx.Timeout(30.0),
        ) as client:
            resp = await client.get(f"/sessions/{session_id}")
            resp.raise_for_status()
            return resp.json().get("status", "running")

    async def cancel(self, session_id: str) -> bool:
        import httpx

        async with httpx.AsyncClient(
            base_url=settings.devin_api_base_url.rstrip("/"),
            headers={"Authorization": f"Bearer {settings.devin_api_key}"},
            timeout=httpx.Timeout(30.0),
        ) as client:
            resp = await client.post(f"/sessions/{session_id}/cancel")
            return resp.is_success

    async def collect(self, session_id: str) -> list[dict[str, Any]]:
        import httpx

        async with httpx.AsyncClient(
            base_url=settings.devin_api_base_url.rstrip("/"),
            headers={"Authorization": f"Bearer {settings.devin_api_key}"},
            timeout=httpx.Timeout(30.0),
        ) as client:
            resp = await client.get(f"/sessions/{session_id}/messages")
            resp.raise_for_status()
            data = resp.json()
            messages = data.get("messages", data) if isinstance(data, dict) else data

        artifacts: list[dict[str, Any]] = []
        for msg in messages:
            if isinstance(msg, dict):
                artifacts.extend(msg.get("attachments", []))
        return artifacts


class APISpokeExecutor(CloudSpokeExecutor):
    """Devin API — lightweight CI/CD integration.  Same HTTP interface as Cloud."""

    spoke = Spoke.API


class CLISpokeExecutor(SpokeExecutor):
    """Devin CLI — local PTY-based execution for air-gapped environments."""

    spoke = Spoke.CLI

    async def execute(self, request: SpokeRequest) -> SpokeSession:
        from uuid import uuid4

        session_id = f"cli-{uuid4().hex[:12]}"
        logger.info("CLI spoke: spawning local session %s", session_id)
        # In production this delegates to src/cli/bridge.py PTY subprocess.
        # The bridge handles stdin/stdout forwarding and crash recovery.
        return SpokeSession(session_id=session_id, spoke=self.spoke, status="running")

    async def status(self, session_id: str) -> str:
        # CLI bridge would check the PTY process status
        return "running"

    async def cancel(self, session_id: str) -> bool:
        logger.info("CLI spoke: cancelling session %s", session_id)
        return True

    async def collect(self, session_id: str) -> list[dict[str, Any]]:
        # CLI bridge collects artifacts from local filesystem
        return []


class ReviewSpokeExecutor(SpokeExecutor):
    """Devin Review — automated PR review with webhook-native interface."""

    spoke = Spoke.REVIEW

    async def execute(self, request: SpokeRequest) -> SpokeSession:
        # Review spoke triggers via the Devin Review webhook / API
        import httpx

        async with httpx.AsyncClient(
            base_url=settings.devin_api_base_url.rstrip("/"),
            headers={"Authorization": f"Bearer {settings.devin_api_key}", "Content-Type": "application/json"},
            timeout=httpx.Timeout(30.0, connect=10.0),
        ) as client:
            payload: dict[str, Any] = {"prompt": request.prompt, "type": "review"}
            if request.repos:
                payload["repos"] = request.repos
            resp = await client.post("/sessions", json=payload)
            resp.raise_for_status()
            data = resp.json()

        session_id = data.get("session_id", data.get("id", "unknown"))
        return SpokeSession(session_id=session_id, spoke=self.spoke, status="queued")

    async def status(self, session_id: str) -> str:
        import httpx

        async with httpx.AsyncClient(
            base_url=settings.devin_api_base_url.rstrip("/"),
            headers={"Authorization": f"Bearer {settings.devin_api_key}"},
            timeout=httpx.Timeout(30.0),
        ) as client:
            resp = await client.get(f"/sessions/{session_id}")
            resp.raise_for_status()
            return resp.json().get("status", "running")

    async def cancel(self, session_id: str) -> bool:
        return True

    async def collect(self, session_id: str) -> list[dict[str, Any]]:
        return []


class IDESpokeExecutor(SpokeExecutor):
    """Devin IDE — human-in-the-loop collaborative execution."""

    spoke = Spoke.IDE

    async def execute(self, request: SpokeRequest) -> SpokeSession:
        from uuid import uuid4

        session_id = f"ide-{uuid4().hex[:12]}"
        logger.info("IDE spoke: interactive session %s (requires human-in-loop)", session_id)
        return SpokeSession(session_id=session_id, spoke=self.spoke, status="running")

    async def status(self, session_id: str) -> str:
        return "running"

    async def cancel(self, session_id: str) -> bool:
        return True

    async def collect(self, session_id: str) -> list[dict[str, Any]]:
        return []


# ---------------------------------------------------------------------------
# Factory
# ---------------------------------------------------------------------------

_EXECUTORS: dict[Spoke, type[SpokeExecutor]] = {
    Spoke.CLOUD: CloudSpokeExecutor,
    Spoke.CLI: CLISpokeExecutor,
    Spoke.API: APISpokeExecutor,
    Spoke.REVIEW: ReviewSpokeExecutor,
    Spoke.IDE: IDESpokeExecutor,
}


def get_spoke_executor(spoke: Spoke) -> SpokeExecutor:
    """Return a concrete executor instance for the given spoke."""
    cls = _EXECUTORS.get(spoke)
    if cls is None:
        raise ValueError(f"No executor registered for spoke: {spoke}")
    return cls()


async def execute_with_fallback(
    primary: Spoke,
    fallback: Spoke | None,
    request: SpokeRequest,
) -> SpokeSession:
    """Execute on the primary spoke; on failure, retry once on the fallback.

    Implements the "max 1 retry, no loops" policy from Section 9.
    """
    executor = get_spoke_executor(primary)
    try:
        return await executor.execute(request)
    except Exception:
        logger.warning("Primary spoke %s failed for task %s", primary, request.task_id, exc_info=True)
        if fallback is None:
            raise
        logger.info("Falling back to spoke %s for task %s", fallback, request.task_id)
        fb_executor = get_spoke_executor(fallback)
        return await fb_executor.execute(request)
