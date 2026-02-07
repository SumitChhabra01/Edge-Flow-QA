"""Explicit wait helpers."""

from __future__ import annotations

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError


def wait_for_selector(page: Page, selector: str, timeout_ms: int) -> None:
    """Wait for selector to be visible."""
    page.wait_for_selector(selector, state="visible", timeout=timeout_ms)


def wait_for_load(page: Page, timeout_ms: int) -> None:
    """Wait for page load state."""
    page.wait_for_load_state(state="load", timeout=timeout_ms)


def is_visible(page: Page, selector: str, timeout_ms: int) -> bool:
    """Return True if selector becomes visible within timeout."""
    try:
        page.wait_for_selector(selector, state="visible", timeout=timeout_ms)
        return True
    except PlaywrightTimeoutError:
        return False
