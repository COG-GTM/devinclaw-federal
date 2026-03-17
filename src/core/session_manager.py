"""Session Manager — Devin API client and session registry.

Implements the session lifecycle from docs/INTEGRATION.md lines 23-38:
  1. create_session(prompt, playbook_id, repos, secrets) -> session_id
  2. poll_status(session_id) -> status
  3. fetch_messages(session_id) -> messages
  4. collect_artifacts(session_id) -> artifacts
  5. cancel_session(session_id)
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

import httpx

from src.config import settings

logger = logging.getLogger("devinclaw.session_manager")


class SessionStatus(StrEnum):
    """Devin session states."""

    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    ESCALATED = "escalated"
    CANCELLED = "cancelled"


@dataclass
class SessionRecord:
    """Internal registry entry for a tracked session."""

    session_id: str
    task_id: str
    user_id: str
    org_id: str
    spoke: str
    skill_name: str
    status: SessionStatus = SessionStatus.QUEUED
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    messages: list[dict[str, Any]] = field(default_factory=list)
    artifacts: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class DevinAPIClient:
    """HTTP client for the Devin v3 REST API."""

    def __init__(self, api_key: str | None = None, base_url: str | None = None) -> None:
        self.api_key = api_key or settings.devin_api_key
        self.base_url = (base_url or settings.devin_api_base_url).rstrip("/")
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                timeout=httpx.Timeout(30.0, connect=10.0),
            )
        return self._client

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def create_session(
        self,
        prompt: str,
        playbook_id: str | None = None,
        repos: list[str] | None = None,
        secrets: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        """Create a new Devin session (POST /v3/sessions)."""
        client = await self._get_client()
        payload: dict[str, Any] = {"prompt": prompt}
        if playbook_id:
            payload["playbook_id"] = playbook_id
        if repos:
            payload["repos"] = repos
        if secrets:
            payload["secrets"] = secrets

        response = await client.post("/sessions", json=payload)
        response.raise_for_status()
        return response.json()

    async def poll_status(self, session_id: str) -> dict[str, Any]:
        """Get session status (GET /v3/sessions/{id})."""
        client = await self._get_client()
        response = await client.get(f"/sessions/{session_id}")
        response.raise_for_status()
        return response.json()

    async def fetch_messages(self, session_id: str) -> list[dict[str, Any]]:
        """Fetch session messages (GET /v3/sessions/{id}/messages)."""
        client = await self._get_client()
        response = await client.get(f"/sessions/{session_id}/messages")
        response.raise_for_status()
        data = response.json()
        return data.get("messages", data) if isinstance(data, dict) else data

    async def collect_artifacts(self, session_id: str) -> list[dict[str, Any]]:
        """Collect session artifacts from messages."""
        messages = await self.fetch_messages(session_id)
        artifacts: list[dict[str, Any]] = []
        for msg in messages:
            if isinstance(msg, dict):
                for attachment in msg.get("attachments", []):
                    artifacts.append(attachment)
                # Check for PR URLs in message body
                body = msg.get("body", "")
                if "github.com" in body and "/pull/" in body:
                    artifacts.append({"type": "pr_url", "content": body})
        return artifacts

    async def cancel_session(self, session_id: str) -> dict[str, Any]:
        """Cancel a running session (POST /v3/sessions/{id}/cancel)."""
        client = await self._get_client()
        response = await client.post(f"/sessions/{session_id}/cancel")
        response.raise_for_status()
        return response.json()


class SessionRegistry:
    """In-memory registry of all tracked sessions.

    In production, this would be backed by PostgreSQL.
    """

    def __init__(self) -> None:
        self._sessions: dict[str, SessionRecord] = {}

    def register(self, record: SessionRecord) -> None:
        """Register a new session."""
        self._sessions[record.session_id] = record
        logger.info("Registered session %s for task %s", record.session_id, record.task_id)

    def get(self, session_id: str) -> SessionRecord | None:
        """Get a session record."""
        return self._sessions.get(session_id)

    def update_status(self, session_id: str, status: SessionStatus) -> None:
        """Update session status."""
        record = self._sessions.get(session_id)
        if record:
            record.status = status
            record.updated_at = datetime.now(UTC)

    def list_active(self) -> list[SessionRecord]:
        """List all active (non-terminal) sessions."""
        active_states = {SessionStatus.QUEUED, SessionStatus.RUNNING, SessionStatus.PAUSED}
        return [s for s in self._sessions.values() if s.status in active_states]

    def list_by_task(self, task_id: str) -> list[SessionRecord]:
        """List all sessions for a given task."""
        return [s for s in self._sessions.values() if s.task_id == task_id]

    def list_by_user(self, user_id: str) -> list[SessionRecord]:
        """List all sessions for a given user."""
        return [s for s in self._sessions.values() if s.user_id == user_id]


class SessionManager:
    """Orchestrates Devin session lifecycle with polling and artifact collection."""

    def __init__(self) -> None:
        self.api_client = DevinAPIClient()
        self.registry = SessionRegistry()

    async def launch_session(
        self,
        task_id: str,
        user_id: str,
        org_id: str,
        prompt: str,
        skill_name: str,
        spoke: str,
        playbook_id: str | None = None,
        repos: list[str] | None = None,
        secrets: dict[str, str] | None = None,
    ) -> SessionRecord:
        """Launch a new Devin session and register it."""
        result = await self.api_client.create_session(
            prompt=prompt,
            playbook_id=playbook_id,
            repos=repos,
            secrets=secrets,
        )

        session_id = result.get("session_id", result.get("id", "unknown"))
        record = SessionRecord(
            session_id=session_id,
            task_id=task_id,
            user_id=user_id,
            org_id=org_id,
            spoke=spoke,
            skill_name=skill_name,
            status=SessionStatus.QUEUED,
        )
        self.registry.register(record)
        return record

    async def poll_until_complete(
        self,
        session_id: str,
        timeout_seconds: int = 3600,
    ) -> SessionRecord:
        """Poll session status until terminal state or timeout."""
        terminal_states = {SessionStatus.COMPLETED, SessionStatus.FAILED, SessionStatus.CANCELLED}
        elapsed = 0
        interval = settings.devin_poll_interval_seconds

        while elapsed < timeout_seconds:
            result = await self.api_client.poll_status(session_id)
            status_str = result.get("status", "running")
            try:
                status = SessionStatus(status_str)
            except ValueError:
                status = SessionStatus.RUNNING

            self.registry.update_status(session_id, status)

            if status in terminal_states:
                record = self.registry.get(session_id)
                if record and status == SessionStatus.COMPLETED:
                    record.artifacts = await self.api_client.collect_artifacts(session_id)
                    record.messages = await self.api_client.fetch_messages(session_id)
                if record:
                    return record

            await asyncio.sleep(interval)
            elapsed += interval

        # Timeout — mark as failed
        self.registry.update_status(session_id, SessionStatus.FAILED)
        record = self.registry.get(session_id)
        if record:
            record.metadata["timeout"] = True
            return record
        msg = f"Session {session_id} not found in registry"
        raise ValueError(msg)

    async def close(self) -> None:
        """Shut down API client."""
        await self.api_client.close()
