"""Storage layer for sensors and readings.

The backing store is an implementation detail (in-memory dict, SQLite,
something else). The interface below is what the rest of the server uses.
"""
from __future__ import annotations

from typing import Iterable, Optional


class Storage:
    """Abstract storage interface."""

    async def add_sensor(self, sensor) -> None:
        """Register a new sensor."""
        raise NotImplementedError

    async def remove_sensor(self, sensor_id: str) -> None:
        """Remove a sensor and (optionally) its readings."""
        raise NotImplementedError

    async def list_sensors(self) -> Iterable:
        """Return all registered sensors."""
        raise NotImplementedError

    async def add_reading(self, reading) -> None:
        """Persist a single reading."""
        raise NotImplementedError

    async def get_readings(
        self,
        sensor_id: str,
        from_ts: Optional[float] = None,
        to_ts: Optional[float] = None,
    ) -> Iterable:
        """Return readings for a sensor within an optional time window."""
        raise NotImplementedError
