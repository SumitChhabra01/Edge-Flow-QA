"""Sample API smoke test."""

from __future__ import annotations

import os

import pytest

from core.api_client import ApiClient
from utils.config_loader import load_config


@pytest.mark.api
def test_get_post():
    """Validate GET /posts/1 returns 200."""
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    config = load_config(root_dir)
    base_url = config["environment"].get("api_base_url", "https://jsonplaceholder.typicode.com")

    client = ApiClient(base_url=base_url, timeout_ms=config["config"]["timeouts"]["api"])
    client.start()
    try:
        response = client.get("/posts/1")
        assert response.status_code == 200
    finally:
        client.stop()
