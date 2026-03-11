"""CLI Stream — real-time output forwarding from PTY to WebSocket.

Reads PTY output, forwards to WebSocket connections,
and buffers output for audit trail storage.
"""

from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any

logger = logging.getLogger("devinclaw.cli_stream")


@dataclass
class StreamBuffer:
    """Buffered output for a CLI session."""

    session_id: str
    lines: list[dict[str, Any]] = field(default_factory=list)
    total_bytes: int = 0
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())

    def append(self, content: str, stream: str = "stdout") -> None:
        """Add output to buffer."""
        self.lines.append({
            "timestamp": datetime.now(UTC).isoformat(),
            "stream": stream,
            "content": content,
        })
        self.total_bytes += len(content)

    def get_audit_trail(self) -> list[dict[str, Any]]:
        """Get the full buffer as an audit trail."""
        return list(self.lines)


class CLIStreamManager:
    """Manages real-time streaming from CLI sessions to WebSocket clients."""

    def __init__(self) -> None:
        self._buffers: dict[str, StreamBuffer] = {}
        self._ws_broadcast_fn: Any = None

    def set_broadcast_function(self, fn: Any) -> None:
        """Set the WebSocket broadcast function."""
        self._ws_broadcast_fn = fn

    def get_or_create_buffer(self, session_id: str) -> StreamBuffer:
        """Get existing buffer or create a new one."""
        if session_id not in self._buffers:
            self._buffers[session_id] = StreamBuffer(session_id=session_id)
        return self._buffers[session_id]

    async def process_output(self, session_id: str, content: str, stream: str = "stdout") -> None:
        """Process CLI output: buffer it and forward to WebSocket."""
        buf = self.get_or_create_buffer(session_id)
        buf.append(content, stream=stream)

        # Forward to WebSocket if broadcast function is set
        if self._ws_broadcast_fn:
            await self._ws_broadcast_fn(session_id, {
                "type": "output",
                "stream": stream,
                "content": content,
                "session_id": session_id,
            })

    async def stream_from_bridge(
        self,
        session_id: str,
        read_fn: Any,
        poll_interval: float = 0.1,
    ) -> None:
        """Continuously read from CLI bridge and stream output.

        Args:
            session_id: Session to stream from
            read_fn: Callable that reads output from the CLI bridge
            poll_interval: Seconds between read attempts
        """
        logger.info("Starting stream for session %s", session_id)

        while True:
            try:
                output = read_fn(session_id)
                if output:
                    await self.process_output(session_id, output)
                else:
                    await asyncio.sleep(poll_interval)
            except Exception:
                logger.exception("Stream error for session %s", session_id)
                break

        logger.info("Stream ended for session %s", session_id)

    def get_buffer(self, session_id: str) -> StreamBuffer | None:
        """Get the buffer for a session."""
        return self._buffers.get(session_id)

    def get_audit_trail(self, session_id: str) -> list[dict[str, Any]]:
        """Get audit trail for a session."""
        buf = self._buffers.get(session_id)
        return buf.get_audit_trail() if buf else []

    def clear_buffer(self, session_id: str) -> None:
        """Clear buffer for a session."""
        self._buffers.pop(session_id, None)
