"""Entry point for the WebSocket live-feed server.

Run with:
    python -m wss
"""
from __future__ import annotations

import contextlib
import asyncio

import websockets

from . import broadcaster as broadcaster_module
from . import handler
from server import storage


async def main() -> None:
    """Boot the WebSocket server.

    Responsibilities:
      - Construct the broadcaster.
      - Subscribe to the source of incoming readings (shared queue, DB poll,
        IPC channel — your design decision).
      - Start the WebSocket server on the configured host/port.
      - Run forever.
    """
    db = storage.SQLiteStorage("telemetry.db")
    broadcaster = broadcaster_module.Broadcaster()

    async def poll_readings() -> None:
        last_id = 0
        while True:
            cursor = db.conn.cursor()
            cursor.execute(
                "SELECT id, sensor_id, reading_type, value, timestamp FROM readings WHERE id > ? ORDER BY id ASC",
                (last_id,),
            )
            rows = cursor.fetchall()
            for row in rows:
                last_id = row["id"]
                await broadcaster.publish(dict(row))
            await asyncio.sleep(1.0)

    async with websockets.serve(
        lambda ws, path=None: handler.live(ws, path, broadcaster),
        "127.0.0.1",
        8765,
    ):
        poll_task = asyncio.create_task(poll_readings())
        try:
            await asyncio.Event().wait()
        finally:
            poll_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await poll_task


if __name__ == "__main__":
    asyncio.run(main())
