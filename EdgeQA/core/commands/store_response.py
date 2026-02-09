"""STORE_RESPONSE command."""

from __future__ import annotations

from core.commands.base_command import BaseCommand


class StoreResponseCommand(BaseCommand):
    """Store last API response JSON into context."""

    name = "STORE_RESPONSE"

    def execute(self, target: str | None, data: str | None, context):
        response_json = context.get("LAST_RESPONSE_JSON", {})
        return response_json
