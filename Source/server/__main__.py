"""Entry point for the telemetry server.

Run with:
    python -m server
"""
from __future__ import annotations
from . import rest_api
from . import storage
from . import tcp_ingest
import asyncio
from aiohttp import web


async def main() -> None:
    """Boot the telemetry server.

    Responsibilities:
      - Initialise the storage layer.
      - Start the TCP ingest listener for sensor connections.
      - Start the aiohttp app hosting the REST API.
      - Wait until shutdown.
    """
    # Initialize the storage layer
    db = storage.SQLiteStorage()
    
    # Update rest_api's global storage instance
    rest_api.storage_instance = db
    
    # Start the TCP ingest server
    tcp_server = await tcp_ingest.start_tcp_server("127.0.0.1", 9999, db)
    
    # Start the REST API
    app = rest_api.build_app()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "127.0.0.1", 8080)
    await site.start()
    
    # Keep servers running
    try:
        await asyncio.Event().wait()
    except KeyboardInterrupt:
        print("Shutting down...")
    finally:
        tcp_server.close()
        await tcp_server.wait_closed()
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
