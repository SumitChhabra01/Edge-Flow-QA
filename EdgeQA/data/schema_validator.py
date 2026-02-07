"""Schema validation utilities for codeless inputs."""

from __future__ import annotations

from typing import Any, Dict

from jsonschema import validate


EXCEL_SCHEMA = {
    "type": "object",
    "properties": {
        "steps": {"type": "array"},
    },
    "required": ["steps"],
}

JSON_SCHEMA = {
    "type": "object",
    "properties": {
        "steps": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "step": {"type": "string"},
                    "action": {"type": "string"},
                    "locator": {"type": ["string", "null"]},
                    "value": {"type": ["string", "null"]},
                    "expected": {"type": ["string", "null"]},
                },
                "required": ["step", "action"],
            },
        }
    },
    "required": ["steps"],
}


def validate_json_schema(payload: Dict[str, Any]) -> None:
    """Validate JSON payload with the predefined schema."""
    validate(instance=payload, schema=JSON_SCHEMA)
