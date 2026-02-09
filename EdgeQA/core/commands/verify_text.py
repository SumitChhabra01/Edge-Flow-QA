"""VERIFY_TEXT command."""

from __future__ import annotations

from core.commands.base_command import BaseCommand


class VerifyTextCommand(BaseCommand):
    """Verify text on a resolved locator."""

    name = "VERIFY_TEXT"

    def execute(self, target: str | None, data: str | None, context):
        page = context.get("page")
        expected = data or ""
        actual = page.text_content(target) or ""
        if actual.strip() != expected.strip():
            raise AssertionError(f"Text mismatch. Expected='{expected}', Actual='{actual.strip()}'")
        return actual
