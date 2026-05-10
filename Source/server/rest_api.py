"""REST API for the telemetry server.

Endpoints:
    GET    /sensors                       list registered sensors
    GET    /sensors/{id}/readings         historical readings  (?from=&to=)
    POST   /sensors                       register a new sensor
    DELETE /sensors/{id}                  remove a sensor

Content negotiation:
    Server-driven via the `Accept` header. Supported media types:
      application/json, application/xml, application/yaml.
    Delegates to server.serialization.

Sessions:
    A cookie identifies the client session — set on first response, read
    on subsequent requests.
"""
from __future__ import annotations
import time
import uuid
from . import serialization
from . import storage
from aiohttp import web


class Sensor:
    """Simple sensor data class."""
    def __init__(self, sensor_id: str, name: str, type: str = None, location: str = None):
        self.id = sensor_id
        self.name = name
        self.type = type
        self.location = location
        self.created_at = time.time()


storage_instance = storage.SQLiteStorage()  # global storage instance for handlers to use
async def list_sensors(request: web.Request) -> web.Response:
    """GET /sensors — list all registered sensors."""
    # Fetch sensor list from storage
    sensors = await storage_instance.list_sensors()
    # Serialize via content negotiation
    media_type = serialization.negotiate(request)
    body = serialization.serialize(sensors, media_type)
    return web.Response(body=body, content_type=media_type)
    


async def get_readings(request: web.Request) -> web.Response:
    """GET /sensors/{id}/readings — historical readings for a sensor."""
    # Parse `from` and `to` query params
    from_time = request.query.get("from")
    to_time = request.query.get("to")
    
    # Convert to float if provided
    from_ts = float(from_time) if from_time else None
    to_ts = float(to_time) if to_time else None
    
    # Query storage
    sensor_id = request.match_info["id"]
    readings = await storage_instance.get_readings(sensor_id, from_ts, to_ts)
    
    # Serialize via content negotiation
    media_type = serialization.negotiate(request)
    body = serialization.serialize(readings, media_type)
    return web.Response(body=body, content_type=media_type)


async def register_sensor(request: web.Request) -> web.Response:
    """POST /sensors — register a new sensor."""
    try:
        # Parse JSON body
        payload = await request.json()
    except Exception:
        return web.Response(status=400, text="Invalid JSON")
    
    # Extract required/optional fields
    sensor_id = payload.get("id")
    name = payload.get("name")
    
    if not sensor_id or not name:
        return web.Response(status=400, text="Missing 'id' or 'name' field")
    
    # Create sensor object
    sensor = Sensor(
        sensor_id=sensor_id,
        name=name,
        type=payload.get("type"),
        location=payload.get("location")
    )
    
    # Add to storage
    await storage_instance.add_sensor(sensor)
    
    # Return 201 Created with Location header
    return web.Response(
        status=201,
        headers={"Location": f"/sensors/{sensor_id}"}
    )


async def delete_sensor(request: web.Request) -> web.Response:
    """DELETE /sensors/{id} — remove a sensor."""
    sensor_id = request.match_info["id"]
    await storage_instance.remove_sensor(sensor_id)
    return web.Response(status=204)


@web.middleware
async def session_cookie_middleware(request: web.Request, handler):
    """Set/read the session cookie on every request."""
    # Read existing cookie or create new session ID
    session_id = request.cookies.get("session_id")
    if not session_id:
        session_id = str(uuid.uuid4())
    
    # Attach session info to request
    request["session_id"] = session_id
    
    # Call the handler
    response = await handler(request)
    
    # Set/refresh the session cookie
    response.set_cookie("session_id", session_id, max_age=86400)
    
    return response


def build_app() -> web.Application:
    """Construct and return the aiohttp Application for the REST API."""
    app = web.Application(middlewares=[session_cookie_middleware])
    app.router.add_get("/sensors", list_sensors)
    app.router.add_get("/sensors/{id}/readings", get_readings)
    app.router.add_post("/sensors", register_sensor)
    app.router.add_delete("/sensors/{id}", delete_sensor)
    return app
