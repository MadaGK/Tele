# IoT Telemetry Pipeline — Source

> Scaffold only. All modules contain stubs — fill in implementation as you build.

## Project layout

```
Source/
├── proto/                  Protobuf schema (.proto)
├── config/                 Sample YAML sensor configuration
├── server/                 Sensor TCP ingest + REST API
├── wss/                    WebSocket server (live feed at /live)
└── client/                 Sensor simulator (TCP client)
```

Each of `server/`, `wss/`, and `client/` is a runnable Python module. They share state through the storage layer — decide how (shared SQLite file, in-process queue, IPC) and document it here.

## Setup

```bash
pip install -r requirements.txt

# Compile the Protobuf schema to Python
protoc --python_out=. proto/telemetry.proto
```

## Running

In three separate terminals, from the `Source/` directory:

```bash
# 1. The telemetry server (TCP ingest + REST API)
python -m server

# 2. The WebSocket live-feed server
python -m wss

# 3. The sensor simulator
python -m client --config config/sensors.yaml
```

## REST API

Endpoints (all support content negotiation via the `Accept` header — JSON, XML, YAML):

| Method | Path                              | Purpose                          |
|--------|-----------------------------------|----------------------------------|
| GET    | `/sensors`                        | List registered sensors          |
| GET    | `/sensors/{id}/readings`          | Historical readings (`?from=&to=`) |
| POST   | `/sensors`                        | Register a new sensor            |
| DELETE | `/sensors/{id}`                   | Remove a sensor                  |

Sessions are tracked via cookies — set on first response, returned by the client on subsequent requests.

## WebSocket

Connect to `ws://<host>:<port>/live`. Send a JSON subscription message after the upgrade to filter on specific sensor IDs. Frames on this channel are JSON.



## AI GENERATED.......... To view the live readings with a websocket 
paste this code in power shell

@'
import asyncio
import websockets

async def main():
    async with websockets.connect("ws://127.0.0.1:8765/live") as ws:
        await ws.send('{"action": "subscribe", "sensors": ["gh-a-temp-01"]}')
        async for msg in ws:
            print(msg)

asyncio.run(main())
'@ | python -

You should see JSON messages stream in for the subscribed sensor ID.


## Authors
Madalitso Kasasi, BSC-COM-NE-17-23
