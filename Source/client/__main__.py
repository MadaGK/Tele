"""Entry point for the sensor simulator.

Run with:
    python -m client --config config/sensors.yaml
"""
from __future__ import annotations

import asyncio


async def main() -> None:
    """Load the YAML config, spawn one task per sensor, run them all."""
    # TODO: parse CLI args (path to YAML config)
    # TODO: load and validate config (server host/port, sensors list)
    # TODO: for each sensor entry, build a SensorSimulator and schedule .run()
    # TODO: asyncio.gather(*tasks)
    raise NotImplementedError


if __name__ == "__main__":
    asyncio.run(main())
