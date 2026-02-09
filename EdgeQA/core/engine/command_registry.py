"""Command registry for DSL engine."""

from __future__ import annotations

from typing import Dict

from core.commands.base_command import BaseCommand


class CommandRegistry:
    """Registry for DSL commands."""

    def __init__(self) -> None:
        self._commands: Dict[str, BaseCommand] = {}

    def register(self, name: str, command: BaseCommand) -> None:
        """Register a command by name."""
        self._commands[name.upper()] = command

    def get(self, name: str) -> BaseCommand:
        """Retrieve a command by name."""
        key = name.upper()
        if key not in self._commands:
            raise ValueError(f"InvalidCommandException: COMMAND '{name}' not supported")
        return self._commands[key]
