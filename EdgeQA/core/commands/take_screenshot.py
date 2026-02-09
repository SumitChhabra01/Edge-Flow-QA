"""TAKE_SCREENSHOT command."""

from __future__ import annotations

import os
from datetime import datetime

from core.commands.base_command import BaseCommand
from core.constants import SCREENSHOTS_DIR_NAME
from utils.file_utils import ensure_dir, resolve_path


class TakeScreenshotCommand(BaseCommand):
    """Capture a full-page screenshot."""

    name = "TAKE_SCREENSHOT"

    def execute(self, target: str | None, data: str | None, context):
        page = context.get("page")
        artifacts_dir = context.get("ARTIFACTS_DIR")
        if not artifacts_dir:
            artifacts_dir = resolve_path(os.getcwd(), "reports", "artifacts")
        screenshots_dir = ensure_dir(os.path.join(artifacts_dir, SCREENSHOTS_DIR_NAME))
        filename = data or f"dsl_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.png"
        if not filename.lower().endswith(".png"):
            filename += ".png"
        path = os.path.join(screenshots_dir, filename)
        page.screenshot(path=path, full_page=True)
        return path
