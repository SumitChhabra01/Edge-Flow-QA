"""File system utilities for EdgeQA."""

from __future__ import annotations

import os
from typing import Iterable


def ensure_dir(path: str) -> str:
    """Ensure the directory exists and return its path."""
    os.makedirs(path, exist_ok=True)
    return path


def ensure_dirs(paths: Iterable[str]) -> None:
    """Ensure multiple directories exist."""
    for path in paths:
        ensure_dir(path)


def resolve_path(root_dir: str, *parts: str) -> str:
    """Resolve a path relative to the framework root."""
    return os.path.join(root_dir, *parts)
