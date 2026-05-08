"""Tracks connected WebSocket clients and dispatches readings to them.

Owns the set of live clients, their subscription filters, and a way for
producers (the telemetry server) to publish a new reading.
"""
from __future__ import annotations


class Broadcaster:
    """Fan-out of readings to the set of connected WebSocket clients."""

    def __init__(self) -> None:
        # TODO: track connected clients and their per-client subscriptions
        raise NotImplementedError

    async def register(self, websocket) -> None:
        """Add a newly connected client."""
        raise NotImplementedError

    async def unregister(self, websocket) -> None:
        """Remove a disconnected client."""
        raise NotImplementedError

    async def set_subscription(self, websocket, sensor_ids) -> None:
        """Replace the per-client sensor-id filter."""
        raise NotImplementedError

    async def publish(self, reading) -> None:
        """Push a reading to every interested client.

        Be careful with slow consumers — a blocked client must not stall
        delivery to the rest. Document the strategy you choose
        (drop, buffer-with-bound, disconnect, etc.) in the architecture
        document.
        """
        # TODO: serialize reading to JSON
        # TODO: for each client whose subscription matches, send concurrently
        # TODO: handle send-timeouts and disconnected clients
        raise NotImplementedError
