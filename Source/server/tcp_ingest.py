from __future__ import annotations

import asyncio
import struct
from typing import Optional

from proto import telemetry_pb2

from . import storage


async def handle_sensor(
    reader: asyncio.StreamReader,
    writer: asyncio.StreamWriter,
    storage_instance: storage.Storage,
    broadcaster=None,
) -> None:
    """Handle one sensor connection until it closes.
    
    Args:
        reader: Async stream reader for sensor data
        writer: Async stream writer for responses
        storage_instance: Storage backend for persisting readings
        broadcaster: Optional broadcaster for live WebSocket updates
    """
    peername = writer.get_extra_info('peername')
    print(f"Sensor connected from {peername}")

    try:
        while True:
            # 1. Read exactly 4 bytes to extract the big-endian length prefix
            header = await reader.readexactly(4)
            
            # Unpack the 4-byte prefix as an unsigned int ('>I' means big-endian uint32)
            (payload_length,) = struct.unpack(">I", header)

            # 2. Read exactly the number of bytes specified by the length prefix
            payload = await reader.readexactly(payload_length)

            try:
                # 3. Decode the protobuf payload
                reading = telemetry_pb2.Reading()
                reading.ParseFromString(payload)

                # 4. Persist to storage
                await storage_instance.add_reading(reading)
                print(f"Received valid reading from {peername}: sensor_id={reading.sensor_id}, value={reading.value}, timestamp={reading.timestamp}")
                
                # 5. Broadcast to live clients (if broadcaster is available)
                if broadcaster:
                    try:
                        await broadcaster.push(reading)
                    except Exception as broadcast_error:
                        print(f"Broadcaster error: {broadcast_error}")

            except Exception as decode_error:
                # Handle malformed frames without dropping the client connection
                print(f"Malformed message from {peername}: {decode_error}")
                continue

    except asyncio.IncompleteReadError:
        # Expected exception when the sensor cleanly closes the connection
        print(f"Sensor {peername} disconnected cleanly.")
    except Exception as network_error:
        # Captures dirty drops, connection resets, or unexpected timeouts
        print(f"Connection error with sensor {peername}: {network_error}")
    finally:
        # Safely shut down the socket resources
        writer.close()
        await writer.wait_closed()


async def start_tcp_server(
    host: str, 
    port: int, 
    storage_instance: storage.Storage,
    broadcaster=None,
) -> asyncio.AbstractServer:
    """Start the TCP ingest server listening on (host, port)."""
    async def handler(reader, writer):
        await handle_sensor(reader, writer, storage_instance, broadcaster)
    
    server = await asyncio.start_server(handler, host, port)
    print(f"TCP server listening on {host}:{port}")
    return server
