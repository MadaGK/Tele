"""WebSocket connection handler at /live.

One coroutine per connected client. Reads optional subscription messages
from the client and otherwise just forwards readings published by the
broadcaster.
"""
from __future__ import annotations

import json


async def live(websocket, path: str | None = None, broadcaster=None) -> None:
    """Handle one WebSocket client connection.

    Protocol on this socket (JSON frames):
      Client -> Server (optional, after upgrade):
          {"action": "subscribe", "sensors": ["sensor-a", "sensor-b"]}
      Server -> Client (continuous):
          {"sensor_id": "...", "type": "...", "value": ..., "ts": ...}
    """
    if broadcaster is None:
        raise RuntimeError("Broadcaster instance is required")

    await broadcaster.register(websocket)
    try:
        async for message in websocket:
            if isinstance(message, bytes):
                continue

            try:
                data = json.loads(message)
            except json.JSONDecodeError:
                continue

            if data.get("action") == "subscribe":
                sensors = data.get("sensors")
                await broadcaster.set_subscription(websocket, sensors)
    finally:
        await broadcaster.unregister(websocket)
