"""API_CALL command."""

from __future__ import annotations

import json
from typing import Any, Dict

from core.commands.base_command import BaseCommand


class ApiCallCommand(BaseCommand):
    """Perform API request using ApiClient."""

    name = "API_CALL"

    def execute(self, target: str | None, data: str | None, context):
        api_client = context.get("api_client")
        if not api_client:
            raise ValueError("API client not configured.")

        method, endpoint, payload = _parse_api_data(target, data)
        response = _dispatch(api_client, method, endpoint, payload)
        context.set("LAST_RESPONSE", response)
        try:
            context.set("LAST_RESPONSE_JSON", response.json())
        except Exception:  # noqa: BLE001
            context.set("LAST_RESPONSE_JSON", {})
        return response


def _dispatch(api_client, method: str, endpoint: str, payload: Dict[str, Any]):
    method_upper = method.upper()
    if method_upper == "GET":
        return api_client.get(endpoint)
    if method_upper == "POST":
        return api_client.post(endpoint, json_body=payload)
    if method_upper == "PUT":
        return api_client.put(endpoint, json_body=payload)
    if method_upper == "DELETE":
        return api_client.delete(endpoint, json_body=payload)
    if method_upper == "PATCH":
        return api_client.patch(endpoint, json_body=payload)
    if method_upper == "HEAD":
        return api_client.head(endpoint)
    raise ValueError(f"InvalidCommandException: COMMAND '{method}' not supported")


def _parse_api_data(target: str | None, data: str | None):
    endpoint = target or ""
    payload: Dict[str, Any] = {}
    method = "GET"

    if data:
        try:
            parsed = json.loads(data)
            method = str(parsed.get("method", method))
            endpoint = str(parsed.get("endpoint", endpoint))
            payload = parsed.get("payload", {}) or {}
            return method, endpoint, payload
        except json.JSONDecodeError:
            pass

        parts = data.split()
        if parts:
            method = parts[0]
            if len(parts) > 1:
                endpoint = parts[1]
    return method, endpoint, payload
