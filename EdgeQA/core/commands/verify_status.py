"""VERIFY_STATUS command."""

from __future__ import annotations

from core.commands.base_command import BaseCommand


class VerifyStatusCommand(BaseCommand):
    """Verify status code of last response."""

    name = "VERIFY_STATUS"

    def execute(self, target: str | None, data: str | None, context):
        response = context.get("LAST_RESPONSE")
        if response is None:
            raise ValueError("No API response available for VERIFY_STATUS.")
        expected = int(data or "200")
        if response.status_code != expected:
            raise AssertionError(f"Status mismatch. Expected={expected}, Actual={response.status_code}")
        return response.status_code
