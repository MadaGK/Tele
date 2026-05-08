"""Content negotiation for the REST API.

Maps the `Accept` header on a request to a serializer for the response.
Supported media types:
    application/json
    application/xml
    application/yaml   (also accepts text/yaml)

Falls back to JSON when no supported type matches.
"""
from __future__ import annotations

from aiohttp import web


def negotiate(request: web.Request) -> str:
    """Return the chosen response media type for `request`."""
    # TODO: parse the Accept header (consider quality values q=...)
    # TODO: pick the best supported match; default to application/json
    raise NotImplementedError


def serialize(payload, media_type: str) -> bytes:
    """Serialize `payload` (a dict or list of dicts) into bytes."""
    # TODO: dispatch on media_type
    # TODO: application/json -> json.dumps(...).encode()
    # TODO: application/xml  -> xml.etree.ElementTree
    # TODO: application/yaml -> yaml.dump(...).encode()
    raise NotImplementedError
