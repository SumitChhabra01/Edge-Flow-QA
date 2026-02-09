"""Playwright lifecycle management."""

from __future__ import annotations

import os
from typing import Dict, Optional

from playwright.sync_api import Browser, BrowserContext, Page, Playwright, sync_playwright

from core.constants import SCREENSHOTS_DIR_NAME, VIDEO_DIR_NAME
from utils.file_utils import ensure_dir


class PlaywrightManager:
    """Manage Playwright browser, context, and page for tests."""

    def __init__(
        self,
        browser_name: str,
        browser_config: Dict[str, object],
        artifacts_dir: str,
        record_video: bool = False,
    ) -> None:
        self.browser_name = browser_name
        self.browser_config = browser_config
        self.artifacts_dir = artifacts_dir
        self.record_video = record_video
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None

    def start(self) -> Page:
        """Start Playwright and create a new page."""
        self.playwright = sync_playwright().start()
        browser_launcher = getattr(self.playwright, self.browser_name)
        self.browser = browser_launcher.launch(
            headless=bool(self.browser_config.get("headless", True)),
            slow_mo=int(self.browser_config.get("slow_mo", 0)),
        )

        context_kwargs = {}
        if self.record_video:
            video_dir = ensure_dir(os.path.join(self.artifacts_dir, VIDEO_DIR_NAME))
            context_kwargs["record_video_dir"] = video_dir
        self.context = self.browser.new_context(**context_kwargs)
        self.page = self.context.new_page()
        return self.page

    def stop(self) -> None:
        """Stop Playwright and close resources."""
        if self.context:
            self.context.close()
        if self.browser:
            self.browser.close()
        if self.playwright:
            self.playwright.stop()

    def screenshot_on_failure(self, test_name: str, full_page: bool = False) -> Optional[str]:
        """Capture a screenshot and return its path."""
        if not self.page:
            return None
        screenshots_dir = ensure_dir(os.path.join(self.artifacts_dir, SCREENSHOTS_DIR_NAME))
        filename = f"{test_name}.png".replace(" ", "_")
        path = os.path.join(screenshots_dir, filename)
        self.page.screenshot(path=path, full_page=full_page)
        return path
