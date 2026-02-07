"""Pytest base fixtures for EdgeQA."""

from __future__ import annotations

import os
from typing import Dict, Generator

import pytest

from core.constants import ENV_VAR_ENV, ENV_VAR_BROWSER
from core.driver_factory import create_playwright_manager
from utils.config_loader import load_config
from utils.file_utils import ensure_dirs, resolve_path
from utils.logger import get_logger


@pytest.fixture(scope="session")
def framework_config() -> Dict[str, object]:
    """Session-scoped framework configuration."""
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return load_config(root_dir)


@pytest.fixture(scope="session")
def logger(framework_config: Dict[str, object]):
    """Session-scoped logger."""
    logs_dir = resolve_path(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")), "logs")
    return get_logger("edgeqa", logs_dir=logs_dir)


@pytest.fixture(scope="function")
def page(framework_config: Dict[str, object], logger) -> Generator:
    """Provide a Playwright page with managed lifecycle."""
    config = framework_config
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    reports_dir = resolve_path(root_dir, "reports")
    artifacts_dir = resolve_path(reports_dir, "artifacts")
    ensure_dirs([reports_dir, artifacts_dir])

    browser_name = os.getenv(ENV_VAR_BROWSER, config["browser_name"])
    browser_config = config["browser"]
    record_video = bool(config["config"]["video"]["enabled"])
    manager = create_playwright_manager(browser_name, browser_config, artifacts_dir, record_video=record_video)
    page_instance = manager.start()

    yield page_instance

    manager.stop()
