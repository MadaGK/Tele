"""Single-sensor simulation logic.

Each simulated sensor:
  - Connects to the telemetry server over TCP.
  - Generates plausible readings on its configured interval.
  - Encodes each reading as a Protobuf message and writes a length-prefixed
    frame on the socket.
  - Reconnects with backoff after transient network failures.
"""
from __future__ import annotations

import asyncio


class SensorSimulator:
    """Simulates one sensor pushing readings to the telemetry server."""

    def __init__(
        self,
        sensor_id: str,
        sensor_type: str,
        interval_seconds: float,
        host: str,
        port: int,
    ) -> None:
        # TODO: store config; initialise any per-type state used by
        #       _generate_reading (e.g. random walk seed, drift)
        raise NotImplementedError

    async def run(self) -> None:
        """Connect, then push readings on the configured interval forever."""
        # TODO: outer loop with reconnect/backoff
        # TODO: open TCP connection (asyncio.open_connection)
        # TODO: inner loop: generate -> encode -> frame -> send -> sleep
        # TODO: on connection error, log and back off before retrying
        raise NotImplementedError

    def _generate_reading(self):
        """Produce a plausible next Reading for this sensor."""
        # TODO: build and return a Protobuf Reading message
        raise NotImplementedError
