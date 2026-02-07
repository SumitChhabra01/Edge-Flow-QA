"""Factory for Playwright manager instances."""

from __future__ import annotations

from typing import Dict

from core.playwright_manager import PlaywrightManager


def create_playwright_manager(
    browser_name: str,
    browser_config: Dict[str, object],
    artifacts_dir: str,
    record_video: bool = False,
) -> PlaywrightManager:
    """Create a PlaywrightManager for the given browser."""
    return PlaywrightManager(
        browser_name=browser_name,
        browser_config=browser_config,
        artifacts_dir=artifacts_dir,
        record_video=record_video,
    )
