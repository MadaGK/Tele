"""Content negotiation for the REST API.

Maps the `Accept` header on a request to a serializer for the response.
Supported media types:
    application/json
    application/xml
    application/yaml   (also accepts text/yaml)

Falls back to JSON when no supported type matches.
"""
from __future__ import annotations
import json
import yaml
import xml.etree.ElementTree as ET
from typing import Union, Any
from aiohttp import web


def negotiate(request: web.Request) -> str:
    """Return the chosen response media type for `request`."""
    supported_types = {
        "application/json": "application/json",
        "application/xml": "application/xml",
        "application/yaml": "application/yaml",
        "text/yaml": "text/yaml",
    }

    for match in request.accept:
        if match.media_type in supported_types:
            if match.media_type == "text/yaml":
                # map text/yaml to application/yaml
                return "application/yaml"
            return supported_types[match.media_type]
    return "application/json"  # default

def _dict_to_xml_element(tag_name: str, data: dict) -> ET.Element:
        """Helper to convert a dict to an XML element."""
        elem = ET.Element(tag_name)
        for key, value in data.items():
            child = ET.SubElement(elem, key)
            child.text = str(value)
        return elem
def serialize(payload, media_type: str) -> bytes:
    """Serialize `payload` (a dict or list of dicts) into bytes."""
    if media_type == "application/json":
        return json.dumps(payload).encode("utf-8")
    elif media_type == "application/xml":
         if isinstance(payload, list):
            root = ET.Element("items")
            for item in payload:
                root.append(_dict_to_xml_element("item", item))
            return ET.tostring(root)
         else:
            root = _dict_to_xml_element("item", payload)
            return ET.tostring(root)
    elif media_type == "application/yaml":
        return yaml.dump(payload).encode("utf-8")
    else:        
        raise ValueError(f"Unsupported media type: {media_type}")
