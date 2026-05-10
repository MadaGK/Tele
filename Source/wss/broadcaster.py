"""Tracks connected WebSocket clients and dispatches readings to them.

Owns the set of live clients, their subscription filters, and a way for
producers (the telemetry server) to publish a new reading.
"""
from __future__ import annotations

import asyncio
import json
from typing import Iterable


def _reading_to_payload(reading) -> dict:
    if isinstance(reading, dict):
        reading_type = reading.get("reading_type")
        if hasattr(reading_type, "name"):
            reading_type = reading_type.name
        return {
            "sensor_id": reading.get("sensor_id"),
            "type": reading_type,
            "value": reading.get("value"),
            "ts": reading.get("timestamp", reading.get("ts")),
        }

    reading_type = getattr(reading, "reading_type", None)
    if hasattr(reading_type, "name"):
        reading_type = reading_type.name
    elif hasattr(reading_type, "value"):
        reading_type = reading_type.value

    return {
        "sensor_id": getattr(reading, "sensor_id", None),
        "type": reading_type,
        "value": getattr(reading, "value", None),
        "ts": getattr(reading, "timestamp", None),
    }


class Broadcaster:
    """Fan-out of readings to the set of connected WebSocket clients."""

    def __init__(self) -> None:
        self._subscriptions: dict[object, set[str] | None] = {}

    async def register(self, websocket) -> None:
        """Add a newly connected client."""
        self._subscriptions[websocket] = None

    async def unregister(self, websocket) -> None:
        """Remove a disconnected client."""
        self._subscriptions.pop(websocket, None)

    async def set_subscription(self, websocket, sensor_ids) -> None:
        """Replace the per-client sensor-id filter."""
        if sensor_ids is None:
            self._subscriptions[websocket] = None
        else:
            self._subscriptions[websocket] = set(sensor_ids)

    async def publish(self, reading) -> None:
        """Push a reading to every interested client.

        Be careful with slow consumers — a blocked client must not stall
        delivery to the rest. Document the strategy you choose
        (drop, buffer-with-bound, disconnect, etc.) in the architecture
        document.
        """
        payload = json.dumps(_reading_to_payload(reading))
        deliveries = []

        for websocket, sensor_ids in list(self._subscriptions.items()):
            if sensor_ids is not None and payload is not None:
                reading_sensor_id = _reading_to_payload(reading)["sensor_id"]
                if reading_sensor_id not in sensor_ids:
                    continue
            deliveries.append(self._send_one(websocket, payload))

        if deliveries:
            await asyncio.gather(*deliveries, return_exceptions=True)

    async def _send_one(self, websocket, payload: str) -> None:
        try:
            await asyncio.wait_for(websocket.send(payload), timeout=2.0)
        except Exception:
            await self.unregister(websocket)
