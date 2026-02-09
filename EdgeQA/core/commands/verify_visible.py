"""VERIFY_VISIBLE command."""

from __future__ import annotations

from core.commands.base_command import BaseCommand


class VerifyVisibleCommand(BaseCommand):
    """Verify element is visible."""

    name = "VERIFY_VISIBLE"

    def execute(self, target: str | None, data: str | None, context):
        page = context.get("page")
        if not page.is_visible(target):
            raise AssertionError(f"Element not visible: {target}")
        return True
