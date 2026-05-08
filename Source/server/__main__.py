"""Entry point for the telemetry server.

Run with:
    python -m server
"""
from __future__ import annotations

import asyncio


async def main() -> None:
    """Boot the telemetry server.

    Responsibilities:
      - Initialise the storage layer.
      - Start the TCP ingest listener for sensor connections.
      - Start the aiohttp app hosting the REST API.
      - Wait until shutdown.
    """
    # TODO: build the Storage instance
    # TODO: start the TCP ingest server (server.tcp_ingest.start_tcp_server)
    # TODO: start the aiohttp REST app (server.rest_api.build_app)
    # TODO: gather both and run forever
    raise NotImplementedError


if __name__ == "__main__":
    asyncio.run(main())
