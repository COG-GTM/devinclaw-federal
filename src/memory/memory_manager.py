"""Memory Manager — four-scope memory system for compound learning.

Scopes: session, user, org, project.
Each memory entry stores learnings from completed sessions
and injects relevant context into new sessions.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

logger = logging.getLogger("devinclaw.memory_manager")


@dataclass
class MemoryEntry:
    """A single memory entry."""

    entry_id: str = field(default_factory=lambda: str(uuid4()))
    scope: str = ""  # session | user | org | project
    scope_id: str = ""  # ID of the scope entity
    key: str = ""
    value: str = ""
    source_session_id: str = ""
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "entry_id": self.entry_id,
            "scope": self.scope,
            "scope_id": self.scope_id,
            "key": self.key,
            "value": self.value,
            "source_session_id": self.source_session_id,
            "created_at": self.created_at,
            "tags": self.tags,
            "metadata": self.metadata,
        }


class MemoryManager:
    """In-memory store for the four-scope memory system.

    In production, this would be backed by PostgreSQL + vector embeddings.
    """

    def __init__(self) -> None:
        self._entries: list[MemoryEntry] = []

    def store(
        self,
        scope: str,
        scope_id: str,
        key: str,
        value: str,
        source_session_id: str = "",
        tags: list[str] | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> MemoryEntry:
        """Write a memory entry."""
        entry = MemoryEntry(
            scope=scope,
            scope_id=scope_id,
            key=key,
            value=value,
            source_session_id=source_session_id,
            tags=tags or [],
            metadata=metadata or {},
        )
        self._entries.append(entry)
        logger.info("Stored memory: scope=%s key=%s", scope, key)
        return entry

    def search(
        self,
        query: str,
        scope: str | None = None,
        scope_id: str | None = None,
        tags: list[str] | None = None,
        limit: int = 10,
    ) -> list[MemoryEntry]:
        """Search memory entries by keyword matching.

        In production, this would use vector similarity search.
        """
        query_lower = query.lower()
        query_tokens = set(query_lower.split())

        results: list[tuple[float, MemoryEntry]] = []

        for entry in self._entries:
            # Filter by scope
            if scope and entry.scope != scope:
                continue
            if scope_id and entry.scope_id != scope_id:
                continue
            if tags and not any(t in entry.tags for t in tags):
                continue

            # Simple keyword relevance scoring
            entry_text = f"{entry.key} {entry.value}".lower()
            entry_tokens = set(entry_text.split())
            overlap = len(query_tokens & entry_tokens)
            if overlap > 0:
                score = overlap / max(len(query_tokens), 1)
                results.append((score, entry))

        # Sort by relevance
        results.sort(key=lambda x: x[0], reverse=True)
        return [entry for _, entry in results[:limit]]

    def get_by_scope(
        self,
        scope: str,
        scope_id: str,
        limit: int = 50,
        offset: int = 0,
    ) -> list[MemoryEntry]:
        """Get all entries for a specific scope."""
        filtered = [e for e in self._entries if e.scope == scope and e.scope_id == scope_id]
        return filtered[offset : offset + limit]

    def get_by_id(self, entry_id: str) -> MemoryEntry | None:
        """Get a specific memory entry by ID."""
        for entry in self._entries:
            if entry.entry_id == entry_id:
                return entry
        return None

    def delete(self, entry_id: str) -> bool:
        """Delete a memory entry."""
        for i, entry in enumerate(self._entries):
            if entry.entry_id == entry_id:
                self._entries.pop(i)
                return True
        return False

    def list_all(self, limit: int = 100, offset: int = 0) -> list[MemoryEntry]:
        """List all memory entries with pagination."""
        return self._entries[offset : offset + limit]

    def count(self) -> int:
        """Total number of memory entries."""
        return len(self._entries)
