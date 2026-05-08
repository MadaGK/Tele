"""Entry point for the WebSocket live-feed server.

Run with:
    python -m wss
"""
from __future__ import annotations

import asyncio


async def main() -> None:
    """Boot the WebSocket server.

    Responsibilities:
      - Construct the broadcaster.
      - Subscribe to the source of incoming readings (shared queue, DB poll,
        IPC channel — your design decision).
      - Start the WebSocket server on the configured host/port.
      - Run forever.
    """
    # TODO: build Broadcaster
    # TODO: connect to the reading source so broadcaster.publish(...) is
    #       called for every new reading the telemetry server receives
    # TODO: start websockets.serve(handler.live, host, port)
    # TODO: await indefinitely
    raise NotImplementedError


if __name__ == "__main__":
    asyncio.run(main())
