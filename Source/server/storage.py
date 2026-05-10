"""Storage layer for sensors and readings.

The backing store is an implementation detail (in-memory dict, SQLite,
something else). The interface below is what the rest of the server uses.
"""
from __future__ import annotations

import sqlite3
from typing import Iterable, Optional


class Storage:
    """SQLite-backed storage for sensors and readings."""

    def __init__(self, db_path: str = "telemetry.db") -> None:
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        """Create database tables if they don't exist."""
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sensors (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                type TEXT,
                location TEXT,
                created_at REAL NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sensor_id TEXT NOT NULL,
                reading_type TEXT,
                value REAL NOT NULL,
                timestamp REAL NOT NULL,
                FOREIGN KEY (sensor_id) REFERENCES sensors(id)
            )
        """)
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_readings_sensor_ts
            ON readings(sensor_id, timestamp)
        """)

        cursor.execute("PRAGMA table_info(readings)")
        columns = {row[1] for row in cursor.fetchall()}
        if "reading_type" not in columns:
            cursor.execute("ALTER TABLE readings ADD COLUMN reading_type TEXT")

        self.conn.commit()

    @staticmethod
    def _sensor_to_dict(sensor) -> dict:
        if isinstance(sensor, dict):
            return sensor
        return {
            "id": getattr(sensor, "id", None),
            "name": getattr(sensor, "name", None),
            "type": getattr(sensor, "type", None),
            "location": getattr(sensor, "location", None),
            "created_at": getattr(sensor, "created_at", None),
        }

    @staticmethod
    def _row_to_dict(row: sqlite3.Row) -> dict:
        return dict(row)

    async def add_sensor(self, sensor) -> None:
        """Register a new sensor."""
        sensor_data = self._sensor_to_dict(sensor)
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO sensors (id, name, type, location, created_at)
            VALUES (?, ?, ?, ?, ?)
        """, (
            sensor_data["id"],
            sensor_data["name"],
            sensor_data.get("type"),
            sensor_data.get("location"),
            sensor_data.get("created_at"),
        ))
        self.conn.commit()

    async def remove_sensor(self, sensor_id: str) -> None:
        """Remove a sensor and its readings."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM readings WHERE sensor_id = ?", (sensor_id,))
        cursor.execute("DELETE FROM sensors WHERE id = ?", (sensor_id,))
        self.conn.commit()

    async def list_sensors(self) -> Iterable:
        """Return all registered sensors."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM sensors")
        return [self._row_to_dict(row) for row in cursor.fetchall()]

    async def add_reading(self, reading) -> None:
        """Persist a single reading."""
        reading_type = getattr(reading, "reading_type", None)
        if hasattr(reading_type, "name"):
            reading_type = reading_type.name
        elif hasattr(reading_type, "value"):
            reading_type = reading_type.value
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO readings (sensor_id, reading_type, value, timestamp)
            VALUES (?, ?, ?, ?)
        """, (
            reading.sensor_id,
            reading_type,
            reading.value,
            reading.timestamp,
        ))
        self.conn.commit()

    async def get_readings(
        self,
        sensor_id: str,
        from_ts: Optional[float] = None,
        to_ts: Optional[float] = None,
    ) -> Iterable:
        """Return readings for a sensor within an optional time window."""
        cursor = self.conn.cursor()
        query = "SELECT * FROM readings WHERE sensor_id = ?"
        params = [sensor_id]

        if from_ts is not None:
            query += " AND timestamp >= ?"
            params.append(from_ts)

        if to_ts is not None:
            query += " AND timestamp <= ?"
            params.append(to_ts)

        query += " ORDER BY timestamp ASC"
        cursor.execute(query, params)
        return [self._row_to_dict(row) for row in cursor.fetchall()]

    def close(self) -> None:
        """Close the database connection."""
        self.conn.close()


class SQLiteStorage(Storage):
    """SQLite-backed storage implementation used by the application."""

    def __init__(self, db_path: str = "telemetry.db") -> None:
        super().__init__(db_path=db_path)
