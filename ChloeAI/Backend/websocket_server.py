"""Async WebSocket server — pushes JSON to Unreal clients."""

from __future__ import annotations

import json
import logging
from typing import Any

from websockets.asyncio.server import ServerConnection

from . import config

logger = logging.getLogger(__name__)

_clients: set[ServerConnection] = set()


async def _register(connection: ServerConnection) -> None:
    _clients.add(connection)
    logger.info("WebSocket client connected (%d total)", len(_clients))


async def _unregister(connection: ServerConnection) -> None:
    _clients.discard(connection)
    logger.info("WebSocket client disconnected (%d total)", len(_clients))


async def handle_client(connection: ServerConnection) -> None:
    await _register(connection)
    try:
        async for _message in connection:
            pass
    except Exception as exc:
        logger.debug("handle_client recv ended: %s", exc)
    finally:
        await _unregister(connection)


async def broadcast_json(data: dict[str, Any]) -> None:
    """Send JSON to all connected clients; drop broken connections."""
    if not _clients:
        logger.warning("broadcast_json: no WebSocket clients connected")
    raw = json.dumps(data, ensure_ascii=False)
    dead: list[ServerConnection] = []
    for ws in list(_clients):
        try:
            await ws.send(raw)
        except Exception as exc:
            logger.debug("send failed, removing client: %s", exc)
            dead.append(ws)
    for ws in dead:
        _clients.discard(ws)


async def broadcast_speech(
    audio_path: str,
    visemes: list[dict[str, Any]],
    text: str,
) -> None:
    """Message shape expected by Unreal."""
    try:
        await broadcast_json(
            {
                "type": "speech",
                "audio_path": audio_path,
                "visemes": visemes,
                "text": text,
            }
        )
    except Exception as exc:
        logger.exception("broadcast_speech failed: %s", exc)


