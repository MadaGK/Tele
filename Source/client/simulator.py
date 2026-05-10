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
import random
import struct
import time

from proto import telemetry_pb2


class SensorSimulator:
    """Simulates one sensor pushing readings to the telemetry server."""

    def __init__(
        self,
        sensor_id: str,
        sensor_type: str,
        reporting_interval: float,
        host: str,
        port: int,
    ) -> None:
        self.sensor_id = sensor_id
        self.sensor_type = sensor_type.lower().strip()
        self.reporting_interval = reporting_interval
        self.host = host
        self.port = port
        self._value = self._initial_value()

    def _initial_value(self) -> float:
        if self.sensor_type == "temperature":
            return random.uniform(18.0, 26.0)
        if self.sensor_type == "humidity":
            return random.uniform(35.0, 70.0)
        if self.sensor_type == "soil_moisture":
            return random.uniform(300.0, 700.0)
        if self.sensor_type == "light":
            return random.uniform(100.0, 800.0)
        if self.sensor_type == "pressure":
            return random.uniform(995.0, 1025.0)
        return random.uniform(0.0, 100.0)

    async def run(self) -> None:
        """Connect, then push readings on the configured interval forever."""
        backoff = 1.0

        while True:
            try:
                reader, writer = await asyncio.open_connection(self.host, self.port)
                print(f"{self.sensor_id}: connected to {self.host}:{self.port}")
                backoff = 1.0

                try:
                    while True:
                        reading = self._generate_reading()
                        payload = reading.SerializeToString()
                        writer.write(struct.pack(">I", len(payload)) + payload)
                        await writer.drain()
                        await asyncio.sleep(self.reporting_interval)
                finally:
                    writer.close()
                    await writer.wait_closed()

            except (ConnectionError, OSError, asyncio.TimeoutError) as exc:
                print(f"{self.sensor_id}: connection failed ({exc}); retrying in {backoff:.1f}s")
                await asyncio.sleep(backoff)
                backoff = min(backoff * 2.0, 30.0)

    def _generate_reading(self):
        """Produce a plausible next Reading for this sensor."""
        drift = {
            "temperature": 0.3,
            "humidity": 1.2,
            "soil_moisture": 8.0,
            "light": 25.0,
            "pressure": 0.6,
        }.get(self.sensor_type, 1.0)

        self._value += random.uniform(-drift, drift)
        self._value = max(0.0, self._value)

        reading = telemetry_pb2.Reading()
        reading.sensor_id = self.sensor_id
        reading.timestamp = int(time.time())
        reading.value = float(self._value)

        enum_name = self.sensor_type.upper()
        enum_value = getattr(telemetry_pb2.ReadingType, enum_name, telemetry_pb2.ReadingType.READING_TYPE_UNSPECIFIED)
        reading.reading_type = enum_value
        return reading
