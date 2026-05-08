"""WebSocket connection handler at /live.

One coroutine per connected client. Reads optional subscription messages
from the client and otherwise just forwards readings published by the
broadcaster.
"""
from __future__ import annotations


async def live(websocket, path: str) -> None:
    """Handle one WebSocket client connection.

    Protocol on this socket (JSON frames):
      Client -> Server (optional, after upgrade):
          {"action": "subscribe", "sensors": ["sensor-a", "sensor-b"]}
      Server -> Client (continuous):
          {"sensor_id": "...", "type": "...", "value": ..., "ts": ...}
    """
    # TODO: register this client with the Broadcaster
    # TODO: read incoming subscription messages and update filters
    # TODO: on disconnect, unregister cleanly
    raise NotImplementedError
