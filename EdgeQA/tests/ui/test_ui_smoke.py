"""Sample UI smoke test."""

from __future__ import annotations

import os

import pytest
from utils.config_loader import load_config


@pytest.mark.ui
def test_example_domain(page):
    """Validate Example Domain title."""
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    config = load_config(root_dir)
    base_url = config["environment"].get("base_url", "https://google.com")

    page.goto(base_url)
    assert "Google" in page.title()
