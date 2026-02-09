"""OPEN_URL command."""

from __future__ import annotations

from core.commands.base_command import BaseCommand


class OpenUrlCommand(BaseCommand):
    """Open a URL."""

    name = "OPEN_URL"

    def execute(self, target: str | None, data: str | None, context):
        page = context.get("page")
        base_url = context.get("BASE_URL", "")
        url = data or target or ""
        if url and not url.startswith("http"):
            if base_url.endswith("/") and url.startswith("/"):
                url = base_url[:-1] + url
            elif not base_url.endswith("/") and not url.startswith("/"):
                url = f"{base_url}/{url}"
            else:
                url = base_url + url
        page.goto(url, timeout=context.get("TIMEOUT_MS", 10000))
        return url
