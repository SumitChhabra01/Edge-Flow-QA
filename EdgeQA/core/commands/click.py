"""CLICK command."""

from __future__ import annotations

from core.commands.base_command import BaseCommand


class ClickCommand(BaseCommand):
    """Click on a resolved locator."""

    name = "CLICK"

    def execute(self, target: str | None, data: str | None, context):
        page = context.get("page")
        page.click(target, timeout=context.get("TIMEOUT_MS", 10000))
        return target
