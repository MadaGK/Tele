"""Entry point for the sensor simulator.

Run with:
    python -m client --config config/sensors.yaml
"""
from __future__ import annotations

import asyncio
import argparse
from pathlib import Path

import yaml

from .simulator import SensorSimulator


async def main() -> None:
    """Load the YAML config, spawn one task per sensor, run them all."""
    parser = argparse.ArgumentParser(description="Telemetry sensor simulator")
    parser.add_argument(
        "--config",
        default="config/sensors.yaml",
        help="Path to the YAML sensor config",
    )
    args = parser.parse_args()

    config_path = Path(args.config)
    with config_path.open("r", encoding="utf-8") as config_file:
        config = yaml.safe_load(config_file)

    server_config = config.get("server", {})
    host = server_config.get("host", "127.0.0.1")
    port = int(server_config.get("port", 9999))

    sensors = config.get("sensors", [])
    if not sensors:
        raise ValueError("No sensors configured")

    tasks = []
    for sensor_config in sensors:
        simulator = SensorSimulator(
            sensor_id=sensor_config["sensor_id"],
            sensor_type=sensor_config["sensor_type"],
            reporting_interval=float(sensor_config["reporting_interval"]),
            host=host,
            port=port,
        )
        tasks.append(asyncio.create_task(simulator.run()))

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
