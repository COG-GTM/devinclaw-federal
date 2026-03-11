"""Audit Writer — structured audit trail with tamper-evident hashing.

Writes audit entries matching audit/audit-template.json format.
SHA-256 hashes each entry for tamper evidence.
Supports file-based (JSONL) and future database-backed storage.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

logger = logging.getLogger("devinclaw.audit_writer")


@dataclass
class AuditEntry:
    """A single audit trail entry per audit/audit-template.json."""

    event_id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    event_type: str = ""  # session_start | session_complete | violation | etc.
    session_id: str = ""
    user_id: str = ""
    org_id: str = ""
    task_description: str = ""
    skill_used: str = ""
    spoke_used: str = ""
    artifacts: dict[str, str] = field(default_factory=dict)
    sdlc_checklist: dict[str, bool] = field(default_factory=dict)
    violations: list[dict[str, Any]] = field(default_factory=list)
    duration_seconds: float = 0.0
    outcome: str = ""  # success | failure | partial
    notes: str = ""
    correlation_id: str = ""
    ip_address: str = ""
    sha256_hash: str = ""

    def compute_hash(self) -> str:
        """Compute SHA-256 hash of the entry for tamper evidence."""
        data = asdict(self)
        data.pop("sha256_hash", None)
        canonical = json.dumps(data, sort_keys=True, default=str)
        self.sha256_hash = hashlib.sha256(canonical.encode()).hexdigest()
        return self.sha256_hash


@dataclass
class EvidencePack:
    """Evidence pack per audit/artifact-schemas/evidence-pack.schema.json."""

    session_id: str
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    skill_id: str = ""
    work_order_id: str = ""
    artifacts: list[dict[str, str]] = field(default_factory=list)
    verification: dict[str, Any] = field(default_factory=dict)
    knowledge_updates: list[dict[str, str]] = field(default_factory=list)
    escalations: list[dict[str, Any]] = field(default_factory=list)
    arena: dict[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "session_id": self.session_id,
            "timestamp": self.timestamp,
            "skill_id": self.skill_id,
            "work_order_id": self.work_order_id,
            "artifacts": self.artifacts,
            "verification": self.verification,
        }
        if self.knowledge_updates:
            result["knowledge_updates"] = self.knowledge_updates
        if self.escalations:
            result["escalations"] = self.escalations
        if self.arena:
            result["arena"] = self.arena
        return result


class AuditWriter:
    """Writes structured audit entries to JSONL files and generates evidence packs."""

    def __init__(self, audit_dir: str = "audit") -> None:
        self.audit_dir = audit_dir
        self._log_dir = os.path.join(audit_dir, "logs")
        self._evidence_dir = os.path.join(audit_dir, "evidence-packs")

    def _ensure_dirs(self) -> None:
        os.makedirs(self._log_dir, exist_ok=True)
        os.makedirs(self._evidence_dir, exist_ok=True)

    def write_entry(self, entry: AuditEntry) -> str:
        """Write an audit entry to the JSONL log file.

        Returns the SHA-256 hash of the entry.
        """
        self._ensure_dirs()
        entry.compute_hash()

        # Write to date-partitioned JSONL
        date_str = datetime.now(UTC).strftime("%Y-%m-%d")
        log_path = os.path.join(self._log_dir, f"audit-{date_str}.jsonl")

        with open(log_path, "a") as f:
            f.write(json.dumps(asdict(entry), default=str) + "\n")

        logger.info("Audit entry %s written (type=%s, hash=%s)", entry.event_id, entry.event_type, entry.sha256_hash)
        return entry.sha256_hash

    def write_evidence_pack(self, pack: EvidencePack) -> str:
        """Write an evidence pack JSON file.

        Returns the file path.
        """
        self._ensure_dirs()
        filename = f"evidence-{pack.session_id}-{pack.timestamp[:10]}.json"
        filepath = os.path.join(self._evidence_dir, filename)

        with open(filepath, "w") as f:
            json.dump(pack.to_dict(), f, indent=2, default=str)

        logger.info("Evidence pack written: %s", filepath)
        return filepath

    def read_entries(
        self,
        date: str | None = None,
        event_type: str | None = None,
        user_id: str | None = None,
        session_id: str | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        """Read audit entries with optional filtering."""
        self._ensure_dirs()
        entries: list[dict[str, Any]] = []

        # Determine which log files to read
        if date:
            log_files = [os.path.join(self._log_dir, f"audit-{date}.jsonl")]
        else:
            log_files = sorted(
                [os.path.join(self._log_dir, f) for f in os.listdir(self._log_dir) if f.endswith(".jsonl")],
                reverse=True,
            )

        for log_path in log_files:
            if not os.path.exists(log_path):
                continue
            with open(log_path) as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        entry = json.loads(line)
                    except json.JSONDecodeError:
                        continue

                    # Apply filters
                    if event_type and entry.get("event_type") != event_type:
                        continue
                    if user_id and entry.get("user_id") != user_id:
                        continue
                    if session_id and entry.get("session_id") != session_id:
                        continue

                    entries.append(entry)

        # Apply pagination
        return entries[offset : offset + limit]

    def hash_file(self, filepath: str) -> str:
        """Compute SHA-256 hash of a file for artifact inventory."""
        sha256 = hashlib.sha256()
        with open(filepath, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()
