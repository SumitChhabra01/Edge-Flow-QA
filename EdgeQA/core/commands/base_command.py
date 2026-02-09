"""Base command interface for DSL engine."""

from __future__ import annotations

from typing import Any


class BaseCommand:
    """Base command class for DSL commands."""

    name: str = ""

    def execute(self, target: str | None, data: str | None, context) -> Any:
        """Execute command with resolved target and data."""
        raise NotImplementedError
