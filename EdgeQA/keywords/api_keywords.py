"""API keyword implementations."""

from __future__ import annotations

import json
from typing import Any, Dict, Optional

from core.api_client import ApiClient
from utils.assertion_utils import assert_equal


class APIKeywords:
    """API keyword library for codeless execution."""

    def __init__(self, api_client: ApiClient) -> None:
        self.api_client = api_client

    def api_get(self, path: str, expected_status: Optional[int] = None) -> Dict[str, Any]:
        """Perform GET and return parsed JSON."""
        response = self.api_client.get(path)
        if expected_status is not None:
            assert_equal(response.status_code, expected_status, "GET status mismatch")
        return _parse_json(response.content)

    def api_post(self, path: str, payload: Dict[str, Any], expected_status: Optional[int] = None) -> Dict[str, Any]:
        """Perform POST and return parsed JSON."""
        response = self.api_client.post(path, json_body=payload)
        if expected_status is not None:
            assert_equal(response.status_code, expected_status, "POST status mismatch")
        return _parse_json(response.content)

    def api_put(self, path: str, payload: Dict[str, Any], expected_status: Optional[int] = None) -> Dict[str, Any]:
        """Perform PUT and return parsed JSON."""
        response = self.api_client.put(path, json_body=payload)
        if expected_status is not None:
            assert_equal(response.status_code, expected_status, "PUT status mismatch")
        return _parse_json(response.content)

    def api_delete(self, path: str, payload: Optional[Dict[str, Any]] = None, expected_status: Optional[int] = None) -> Dict[str, Any]:
        """Perform DELETE and return parsed JSON."""
        response = self.api_client.delete(path, json_body=payload)
        if expected_status is not None:
            assert_equal(response.status_code, expected_status, "DELETE status mismatch")
        return _parse_json(response.content)

    def api_patch(self, path: str, payload: Dict[str, Any], expected_status: Optional[int] = None) -> Dict[str, Any]:
        """Perform PATCH and return parsed JSON."""
        response = self.api_client.patch(path, json_body=payload)
        if expected_status is not None:
            assert_equal(response.status_code, expected_status, "PATCH status mismatch")
        return _parse_json(response.content)

    def api_head(self, path: str, expected_status: Optional[int] = None) -> Dict[str, Any]:
        """Perform HEAD and return parsed JSON."""
        response = self.api_client.head(path)
        if expected_status is not None:
            assert_equal(response.status_code, expected_status, "HEAD status mismatch")
        return _parse_json(response.content)


def _parse_json(content: bytes) -> Dict[str, Any]:
    if not content:
        return {}
    return json.loads(content.decode("utf-8"))
