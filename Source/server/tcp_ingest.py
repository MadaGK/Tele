"""Asynchronous TCP listener for sensor connections.

Sensors connect over TCP and stream Protobuf-encoded readings. This module:
  - Accepts connections concurrently with asyncio.start_server.
  - Frames and decodes each Protobuf message from the byte stream.
  - Hands decoded readings to the storage layer (and optionally to a
    broadcaster so the WebSocket /live feed can push them).
  - Tolerates disconnects and malformed messages without crashing the server.

Framing convention: 4-byte big-endian length prefix followed by the Protobuf
payload of that length. Adjust if your design uses a different framing scheme.
"""
from __future__ import annotations

import asyncio


async def handle_sensor(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
) -> None:
    """Handle one sensor connection until it closes."""
    # TODO: read length-prefixed Protobuf frames in a loop
    # TODO: decode each into a Reading message
    # TODO: persist via storage; publish to the live broadcaster
    # TODO: handle malformed frames without dropping the connection
    raise NotImplementedError


async def start_tcp_server(host: str, port: int) -> asyncio.AbstractServer:
    """Start the TCP ingest server listening on (host, port)."""
    # TODO: return await asyncio.start_server(handle_sensor, host, port)
    raise NotImplementedError
