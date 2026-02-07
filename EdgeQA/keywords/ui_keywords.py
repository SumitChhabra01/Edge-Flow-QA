"""UI keyword implementations for Playwright."""

from __future__ import annotations

from playwright.sync_api import Page

from utils.assertion_utils import assert_equal, assert_true
from utils.wait_utils import is_visible, wait_for_selector


class UIKeywords:
    """UI keyword library for codeless execution."""

    def __init__(self, page: Page, timeout_ms: int) -> None:
        self.page = page
        self.timeout_ms = timeout_ms

    def open_url(self, url: str) -> None:
        """Open the specified URL."""
        self.page.goto(url, timeout=self.timeout_ms)

    def click(self, locator: str) -> None:
        """Click on an element."""
        wait_for_selector(self.page, locator, self.timeout_ms)
        self.page.click(locator, timeout=self.timeout_ms)

    def fill_text(self, locator: str, value: str) -> None:
        """Fill text into an input element."""
        wait_for_selector(self.page, locator, self.timeout_ms)
        self.page.fill(locator, value, timeout=self.timeout_ms)

    def select_dropdown(self, locator: str, value: str) -> None:
        """Select a value in a dropdown."""
        wait_for_selector(self.page, locator, self.timeout_ms)
        self.page.select_option(locator, value=value)

    def hover(self, locator: str) -> None:
        """Hover over an element."""
        wait_for_selector(self.page, locator, self.timeout_ms)
        self.page.hover(locator)

    def wait_for_element(self, locator: str) -> None:
        """Wait for an element to be visible."""
        wait_for_selector(self.page, locator, self.timeout_ms)

    def assert_text(self, locator: str, expected: str) -> None:
        """Assert element text equals expected."""
        wait_for_selector(self.page, locator, self.timeout_ms)
        actual = self.page.text_content(locator) or ""
        assert_equal(actual.strip(), expected.strip(), "Text assertion failed")

    def assert_visible(self, locator: str) -> None:
        """Assert element visibility."""
        visible = is_visible(self.page, locator, self.timeout_ms)
        assert_true(visible, f"Element not visible: {locator}")
