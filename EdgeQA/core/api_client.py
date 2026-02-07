"""API client using Playwright request context with Requests fallback."""

from __future__ import annotations

from typing import Any, Dict, Optional

import requests
from playwright.sync_api import APIRequestContext, Playwright, sync_playwright


class ApiClient:
    """API client abstraction for EdgeQA."""

    def __init__(self, base_url: str, timeout_ms: int, playwright: Optional[Playwright] = None) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout_ms = timeout_ms
        self.playwright: Optional[Playwright] = playwright
        self._owns_playwright = playwright is None
        self.request_context: Optional[APIRequestContext] = None

    def start(self) -> None:
        """Start Playwright API request context."""
        if self.playwright is None:
            self.playwright = sync_playwright().start()
        self.request_context = self.playwright.request.new_context(base_url=self.base_url, timeout=self.timeout_ms)

    def stop(self) -> None:
        """Stop Playwright API context."""
        if self.request_context:
            self.request_context.dispose()
        if self.playwright and self._owns_playwright:
            self.playwright.stop()

    def get(self, path: str, params: Optional[Dict[str, Any]] = None) -> requests.Response:
        """Perform GET request."""
        if self.request_context:
            response = self.request_context.get(path, params=params)
            return _to_requests_response(response)
        return requests.get(f"{self.base_url}{path}", params=params, timeout=self.timeout_ms / 1000)

    def post(self, path: str, json_body: Optional[Dict[str, Any]] = None) -> requests.Response:
        """Perform POST request."""
        if self.request_context:
            response = self.request_context.post(path, json=json_body)
            return _to_requests_response(response)
        return requests.post(f"{self.base_url}{path}", json=json_body, timeout=self.timeout_ms / 1000)

    def put(self, path: str, json_body: Optional[Dict[str, Any]] = None) -> requests.Response:
        """Perform PUT request."""
        if self.request_context:
            response = self.request_context.put(path, json=json_body)
            return _to_requests_response(response)
        return requests.put(f"{self.base_url}{path}", json=json_body, timeout=self.timeout_ms / 1000)

    def delete(self, path: str, json_body: Optional[Dict[str, Any]] = None) -> requests.Response:
        """Perform DELETE request."""
        if self.request_context:
            response = self.request_context.delete(path, json=json_body)
            return _to_requests_response(response)
        return requests.delete(f"{self.base_url}{path}", json=json_body, timeout=self.timeout_ms / 1000)


def _to_requests_response(playwright_response) -> requests.Response:
    """Convert Playwright response to requests.Response compatible object."""
    response = requests.Response()
    response.status_code = playwright_response.status
    response._content = playwright_response.body()
    response.headers = playwright_response.headers
    response.url = playwright_response.url
    return response
