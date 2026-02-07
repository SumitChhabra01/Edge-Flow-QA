"""Configuration loader for EdgeQA."""

from __future__ import annotations

import os
from typing import Any, Dict

import yaml

from core.constants import DEFAULT_ENV, DEFAULT_BROWSER, ENV_VAR_ENV, ENV_VAR_BROWSER


def _read_yaml(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def load_config(root_dir: str) -> Dict[str, Any]:
    """Load framework configuration from YAML files."""
    config_path = os.path.join(root_dir, "config", "config.yaml")
    envs_path = os.path.join(root_dir, "config", "environments.yaml")
    browsers_path = os.path.join(root_dir, "config", "browsers.yaml")

    config = _read_yaml(config_path)
    envs = _read_yaml(envs_path)
    browsers = _read_yaml(browsers_path)

    env_name = os.getenv(ENV_VAR_ENV, DEFAULT_ENV)
    browser_name = os.getenv(ENV_VAR_BROWSER, DEFAULT_BROWSER)

    selected_env = envs.get(env_name, {})
    selected_browser = browsers.get(browser_name, {})

    return {
        "config": config,
        "env_name": env_name,
        "browser_name": browser_name,
        "environment": selected_env,
        "browser": selected_browser,
        "all_environments": envs,
        "all_browsers": browsers,
    }
