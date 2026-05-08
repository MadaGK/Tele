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

from aiohttp import web


async def list_sensors(request: web.Request) -> web.Response:
    """GET /sensors — list all registered sensors."""
    # TODO: fetch sensor list from storage
    # TODO: serialize via content negotiation
    raise NotImplementedError


async def get_readings(request: web.Request) -> web.Response:
    """GET /sensors/{id}/readings — historical readings for a sensor."""
    # TODO: parse `from` and `to` query params
    # TODO: query storage
    # TODO: serialize via content negotiation
    raise NotImplementedError


async def register_sensor(request: web.Request) -> web.Response:
    """POST /sensors — register a new sensor."""
    # TODO: parse body (respect Content-Type)
    # TODO: create sensor in storage
    # TODO: return 201 Created with Location header
    raise NotImplementedError


async def delete_sensor(request: web.Request) -> web.Response:
    """DELETE /sensors/{id} — remove a sensor."""
    # TODO: delete from storage
    # TODO: return 204 No Content
    raise NotImplementedError


@web.middleware
async def session_cookie_middleware(request: web.Request, handler):
    """Set/read the session cookie on every request."""
    # TODO: read existing cookie; assign one if missing
    # TODO: attach session info to request for handlers
    # TODO: ensure response sets the cookie when newly issued
    raise NotImplementedError


def build_app() -> web.Application:
    """Construct and return the aiohttp Application for the REST API."""
    # TODO: app = web.Application(middlewares=[session_cookie_middleware])
    # TODO: app.router.add_get("/sensors", list_sensors)
    # TODO: app.router.add_get("/sensors/{id}/readings", get_readings)
    # TODO: app.router.add_post("/sensors", register_sensor)
    # TODO: app.router.add_delete("/sensors/{id}", delete_sensor)
    # TODO: return app
    raise NotImplementedError
