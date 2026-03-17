"""Devin CLI Bridge — spawn and manage CLI as PTY subprocess.

Spawns Devin CLI as a pseudo-terminal, sends input to stdin,
captures stdout/stderr, handles lifecycle with error recovery.
"""

from __future__ import annotations

import asyncio
import contextlib
import logging
import os
import pty
import signal
import subprocess
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

from src.config import settings

logger = logging.getLogger("devinclaw.cli_bridge")


@dataclass
class CLISession:
    """A running Devin CLI PTY session."""

    session_id: str
    pid: int = 0
    fd: int = -1
    status: str = "starting"  # starting | running | stopped | crashed
    started_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    output_buffer: list[str] = field(default_factory=list)
    error_count: int = 0
    max_retries: int = 3
    metadata: dict[str, Any] = field(default_factory=dict)


class CLIBridge:
    """Manages Devin CLI PTY sessions.

    Spawns CLI as a pseudo-terminal subprocess, supports multiple
    concurrent sessions, and provides error recovery with auto-retry.
    """

    def __init__(self, cli_path: str | None = None) -> None:
        self.cli_path = cli_path or settings.devin_cli_path
        self._sessions: dict[str, CLISession] = {}
        self._read_tasks: dict[str, asyncio.Task[None]] = {}

    def spawn(self, session_id: str, initial_command: str = "") -> CLISession:
        """Spawn a new Devin CLI PTY session.

        Uses pty.openpty() to create a pseudo-terminal pair,
        then forks the CLI process connected to the PTY.
        """
        session = CLISession(session_id=session_id)

        try:
            # Create PTY pair
            master_fd, slave_fd = pty.openpty()

            # Spawn CLI process
            env = os.environ.copy()
            env["TERM"] = "xterm-256color"
            env["COLUMNS"] = "120"
            env["LINES"] = "40"

            cmd = [self.cli_path]
            if initial_command:
                cmd.extend(["--exec", initial_command])

            process = subprocess.Popen(
                cmd,
                stdin=slave_fd,
                stdout=slave_fd,
                stderr=slave_fd,
                preexec_fn=os.setsid,
                env=env,
            )

            os.close(slave_fd)  # Close slave in parent

            session.pid = process.pid
            session.fd = master_fd
            session.status = "running"

            self._sessions[session_id] = session
            logger.info("CLI session %s spawned (pid=%d)", session_id, process.pid)

        except FileNotFoundError:
            logger.warning("Devin CLI not found at %s — session %s in mock mode", self.cli_path, session_id)
            session.status = "running"
            session.metadata["mock"] = True
            self._sessions[session_id] = session

        except Exception:
            logger.exception("Failed to spawn CLI for session %s", session_id)
            session.status = "crashed"
            self._sessions[session_id] = session

        return session

    def send_input(self, session_id: str, data: str) -> bool:
        """Send input to a CLI session's stdin."""
        session = self._sessions.get(session_id)
        if not session or session.status != "running":
            return False

        if session.metadata.get("mock"):
            session.output_buffer.append(f"[mock] {data}")
            return True

        if session.fd < 0:
            return False

        try:
            os.write(session.fd, data.encode())
            return True
        except OSError:
            logger.error("Failed to write to CLI session %s", session_id)
            session.status = "crashed"
            return False

    def read_output(self, session_id: str, max_bytes: int = 4096) -> str:
        """Read available output from a CLI session."""
        session = self._sessions.get(session_id)
        if not session or session.status != "running":
            return ""

        if session.metadata.get("mock"):
            if session.output_buffer:
                output = "\n".join(session.output_buffer)
                session.output_buffer.clear()
                return output
            return ""

        if session.fd < 0:
            return ""

        try:
            data = os.read(session.fd, max_bytes)
            output = data.decode("utf-8", errors="replace")
            session.output_buffer.append(output)
            return output
        except OSError:
            return ""

    def stop(self, session_id: str) -> bool:
        """Gracefully stop a CLI session."""
        session = self._sessions.get(session_id)
        if not session:
            return False

        if session.pid > 0:
            try:
                os.killpg(os.getpgid(session.pid), signal.SIGTERM)
            except ProcessLookupError:
                pass
            except OSError:
                logger.warning("Failed to kill CLI process %d", session.pid)

        if session.fd >= 0:
            with contextlib.suppress(OSError):
                os.close(session.fd)

        session.status = "stopped"
        logger.info("CLI session %s stopped", session_id)
        return True

    def restart(self, session_id: str, command: str = "") -> CLISession | None:
        """Restart a crashed CLI session with auto-retry."""
        session = self._sessions.get(session_id)
        if not session:
            return None

        if session.error_count >= session.max_retries:
            logger.error("CLI session %s exceeded max retries (%d)", session_id, session.max_retries)
            return None

        session.error_count += 1
        self.stop(session_id)

        logger.info("Restarting CLI session %s (attempt %d/%d)", session_id, session.error_count, session.max_retries)
        return self.spawn(session_id, initial_command=command)

    def get_session(self, session_id: str) -> CLISession | None:
        """Get a CLI session by ID."""
        return self._sessions.get(session_id)

    def list_sessions(self) -> list[CLISession]:
        """List all CLI sessions."""
        return list(self._sessions.values())

    def cleanup(self) -> None:
        """Stop all sessions and clean up resources."""
        for session_id in list(self._sessions.keys()):
            self.stop(session_id)
        self._sessions.clear()
