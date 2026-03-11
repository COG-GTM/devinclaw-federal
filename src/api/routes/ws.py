"""WebSocket routes — terminal streaming for Devin CLI bridge.

/ws/terminal/{session_id} — bidirectional I/O for CLI sessions
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from src.auth.jwt import TokenError, verify_token

logger = logging.getLogger("devinclaw.ws")

router = APIRouter(tags=["websocket"])

# Active WebSocket connections per session
_connections: dict[str, list[WebSocket]] = {}


async def _authenticate_ws(websocket: WebSocket) -> dict[str, Any] | None:
    """Authenticate WebSocket via query param or first message."""
    # Try query param
    token = websocket.query_params.get("token")
    if token:
        try:
            client_ip = websocket.client.host if websocket.client else "unknown"
            return verify_token(token, request_ip=client_ip)
        except TokenError:
            return None

    # Wait for first message with token
    try:
        data = await asyncio.wait_for(websocket.receive_json(), timeout=10.0)
        token = data.get("token", "")
        if token:
            client_ip = websocket.client.host if websocket.client else "unknown"
            return verify_token(token, request_ip=client_ip)
    except (TimeoutError, TokenError, Exception):
        return None

    return None


@router.websocket("/ws/terminal/{session_id}")
async def terminal_websocket(websocket: WebSocket, session_id: str) -> None:
    """Bidirectional WebSocket for Devin CLI terminal streaming.

    - User types → CLI stdin
    - CLI stdout → user's browser
    - Heartbeat + reconnection support
    """
    await websocket.accept()

    # Authenticate
    claims = await _authenticate_ws(websocket)
    if not claims:
        await websocket.send_json({"type": "error", "message": "Authentication failed"})
        await websocket.close(code=4001, reason="Authentication failed")
        return

    user_id = claims.get("sub", "unknown")
    logger.info("WebSocket connected: session=%s user=%s", session_id, user_id)

    # Register connection
    if session_id not in _connections:
        _connections[session_id] = []
    _connections[session_id].append(websocket)

    # Send connection confirmation
    await websocket.send_json({
        "type": "connected",
        "session_id": session_id,
        "user_id": user_id,
    })

    try:
        while True:
            # Receive message from client
            try:
                data = await asyncio.wait_for(websocket.receive_json(), timeout=300.0)
            except TimeoutError:
                # Send heartbeat
                await websocket.send_json({"type": "heartbeat"})
                continue

            msg_type = data.get("type", "")

            if msg_type == "input":
                # Forward user input to CLI bridge
                input_text = data.get("content", "")
                logger.debug("WS input [%s]: %s", session_id, input_text[:50])

                # In production, this would forward to the CLI bridge PTY
                await websocket.send_json({
                    "type": "output",
                    "content": f"[echo] {input_text}\n",
                    "session_id": session_id,
                })

            elif msg_type == "heartbeat":
                await websocket.send_json({"type": "heartbeat_ack"})

            elif msg_type == "resize":
                # Terminal resize event
                cols = data.get("cols", 80)
                rows = data.get("rows", 24)
                logger.debug("WS resize [%s]: %dx%d", session_id, cols, rows)

    except WebSocketDisconnect:
        logger.info("WebSocket disconnected: session=%s user=%s", session_id, user_id)
    except Exception:
        logger.exception("WebSocket error: session=%s", session_id)
    finally:
        # Clean up connection
        if session_id in _connections:
            _connections[session_id] = [ws for ws in _connections[session_id] if ws != websocket]
            if not _connections[session_id]:
                del _connections[session_id]


async def broadcast_to_session(session_id: str, message: dict[str, Any]) -> None:
    """Broadcast a message to all WebSocket connections for a session."""
    connections = _connections.get(session_id, [])
    for ws in connections:
        try:
            await ws.send_json(message)
        except Exception:
            logger.warning("Failed to send to WebSocket for session %s", session_id)
