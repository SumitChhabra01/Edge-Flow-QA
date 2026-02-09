"""TYPE command."""

from __future__ import annotations

from core.commands.base_command import BaseCommand


class TypeTextCommand(BaseCommand):
    """Type text into a resolved locator."""

    name = "TYPE"

    def execute(self, target: str | None, data: str | None, context):
        page = context.get("page")
        page.fill(target, data or "", timeout=context.get("TIMEOUT_MS", 10000))
        return data
