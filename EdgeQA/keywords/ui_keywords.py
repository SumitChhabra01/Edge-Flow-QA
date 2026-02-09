"""UI keyword implementations for Playwright."""

from __future__ import annotations

import os
import time
from datetime import datetime
from typing import Optional

from playwright.sync_api import Page

from core.constants import SCREENSHOTS_DIR_NAME
from utils.assertion_utils import assert_equal, assert_true
from utils.file_utils import ensure_dir
from utils.wait_utils import is_visible, wait_for_selector


class UIKeywords:
    """UI keyword library for codeless execution."""

    def __init__(
        self,
        page: Page,
        timeout_ms: int,
        artifacts_dir: Optional[str] = None,
        manager=None,
    ) -> None:
        self.page = page
        self.timeout_ms = timeout_ms
        self.artifacts_dir = artifacts_dir
        self.manager = manager
        self._pages = [page]
        self._frame = None

    def open_url(self, url: str) -> None:
        """Open the specified URL."""
        self.page.goto(url, timeout=self.timeout_ms)

    def click(self, locator: str) -> None:
        """Click on an element."""
        self._wait_for(locator)
        self._locator(locator).click(timeout=self.timeout_ms)

    def double_click(self, locator: str) -> None:
        """Double-click on an element."""
        self._wait_for(locator)
        self._locator(locator).dblclick(timeout=self.timeout_ms)

    def right_click(self, locator: str) -> None:
        """Right-click on an element."""
        self._wait_for(locator)
        self._locator(locator).click(button="right", timeout=self.timeout_ms)

    def fill_text(self, locator: str, value: str) -> None:
        """Fill text into an input element."""
        self._wait_for(locator)
        self._locator(locator).fill(value, timeout=self.timeout_ms)

    def clear_text(self, locator: str) -> None:
        """Clear text from an input element."""
        self._wait_for(locator)
        self._locator(locator).fill("", timeout=self.timeout_ms)

    def press_key(self, locator: str, key: str) -> None:
        """Press a key on an element."""
        self._wait_for(locator)
        self._locator(locator).press(key, timeout=self.timeout_ms)

    def select_dropdown(self, locator: str, value: str) -> None:
        """Select a value in a dropdown."""
        self._wait_for(locator)
        self._locator(locator).select_option(value=value)

    def hover(self, locator: str) -> None:
        """Hover over an element."""
        self._wait_for(locator)
        self._locator(locator).hover()

    def scroll_to(self, locator: str) -> None:
        """Scroll to an element."""
        self._wait_for(locator)
        self._locator(locator).scroll_into_view_if_needed()

    def wait_for_element(self, locator: str) -> None:
        """Wait for an element to be visible."""
        self._wait_for(locator)

    def wait_for_visible(self, locator: str) -> None:
        """Wait for an element to be visible."""
        self._locator(locator).wait_for(state="visible", timeout=self.timeout_ms)

    def wait_for_hidden(self, locator: str) -> None:
        """Wait for an element to be hidden."""
        self._locator(locator).wait_for(state="hidden", timeout=self.timeout_ms)

    def wait_for_attached(self, locator: str) -> None:
        """Wait for an element to be attached to DOM."""
        self._locator(locator).wait_for(state="attached", timeout=self.timeout_ms)

    def wait_for_detached(self, locator: str) -> None:
        """Wait for an element to be detached from DOM."""
        self._locator(locator).wait_for(state="detached", timeout=self.timeout_ms)

    def wait_for_enabled(self, locator: str) -> None:
        """Wait for an element to be enabled."""
        self._wait_for_enabled_state(locator, True)

    def wait_for_disabled(self, locator: str) -> None:
        """Wait for an element to be disabled."""
        self._wait_for_enabled_state(locator, False)

    def wait_for_text(self, locator: str, text: str) -> None:
        """Wait for an element to contain text."""
        self._locator(locator).filter(has_text=text).first.wait_for(state="visible", timeout=self.timeout_ms)

    def assert_text(self, locator: str, expected: str) -> None:
        """Assert element text equals expected."""
        self._wait_for(locator)
        actual = self._locator(locator).text_content() or ""
        assert_equal(actual.strip(), expected.strip(), "Text assertion failed")

    def assert_contains_text(self, locator: str, expected: str) -> None:
        """Assert element text contains expected."""
        self._wait_for(locator)
        actual = self._locator(locator).text_content() or ""
        assert_true(expected.strip() in actual.strip(), "Text containment assertion failed")

    def assert_visible(self, locator: str) -> None:
        """Assert element visibility."""
        visible = is_visible(self.page, locator, self.timeout_ms)
        assert_true(visible, f"Element not visible: {locator}")

    def assert_title(self, expected: str) -> None:
        """Assert page title equals expected."""
        actual = self.page.title()
        assert_equal(actual.strip(), expected.strip(), "Title assertion failed")

    def screenshot_full_page(self, filename: Optional[str] = None) -> str:
        """Capture a full-page screenshot."""
        path = self._screenshot_path(filename)
        self.page.screenshot(path=path, full_page=True)
        return path

    def screenshot_element(self, locator: str, filename: Optional[str] = None) -> str:
        """Capture a screenshot of a specific element."""
        self._wait_for(locator)
        path = self._screenshot_path(filename)
        self._locator(locator).screenshot(path=path)
        return path

    def browser_back(self) -> None:
        """Navigate back."""
        self.page.go_back(timeout=self.timeout_ms)

    def browser_refresh(self) -> None:
        """Refresh the current page."""
        self.page.reload(timeout=self.timeout_ms)

    def wait_for_url(self, url_or_pattern: str) -> None:
        """Wait for the page URL to match."""
        if not url_or_pattern:
            raise ValueError("wait_for_url requires a URL or pattern.")
        self.page.wait_for_url(url_or_pattern, timeout=self.timeout_ms)

    def wait_for_load_state(self, state: str = "load") -> None:
        """Wait for the given page load state."""
        self.page.wait_for_load_state(state=state or "load", timeout=self.timeout_ms)

    def new_tab(self, url: Optional[str] = None) -> None:
        """Open a new tab and optionally navigate to a URL."""
        context = self.page.context
        new_page = context.new_page()
        self._pages.append(new_page)
        self._set_page(new_page)
        if url:
            new_page.goto(url, timeout=self.timeout_ms)

    def switch_window(self, index: int) -> None:
        """Switch to a tab/window by index."""
        if index < 0 or index >= len(self._pages):
            raise ValueError(f"Window index out of range: {index}")
        self._set_page(self._pages[index])

    def close_tab(self, index: Optional[int] = None) -> None:
        """Close a tab and switch to the last remaining tab."""
        if not self._pages:
            return
        target_index = index if index is not None else len(self._pages) - 1
        if target_index < 0 or target_index >= len(self._pages):
            raise ValueError(f"Window index out of range: {target_index}")
        page = self._pages.pop(target_index)
        page.close()
        if self._pages:
            self._set_page(self._pages[-1])

    def launch_incognito_mode(self) -> None:
        """Launch a new incognito context and switch to it."""
        browser = self.page.context.browser
        if not browser:
            raise RuntimeError("Browser is not available to create incognito context.")
        context = browser.new_context()
        new_page = context.new_page()
        self._pages = [new_page]
        self._set_page(new_page)

    def switch_to_frame(self, frame_locator: str) -> None:
        """Switch to a frame by locator."""
        wait_for_selector(self.page, frame_locator, self.timeout_ms)
        self._frame = self.page.frame_locator(frame_locator)

    def switch_to_main_frame(self) -> None:
        """Return to the main frame."""
        self._frame = None

    def maximize_window(self) -> None:
        """Maximize browser window when supported."""
        self.page.evaluate("() => { window.moveTo(0,0); window.resizeTo(screen.width, screen.height); }")

    def _set_page(self, page: Page) -> None:
        self.page = page
        if self.manager:
            self.manager.page = page

    def _wait_for(self, locator: str) -> None:
        if self._frame:
            self._locator(locator).wait_for(state="visible", timeout=self.timeout_ms)
        else:
            wait_for_selector(self.page, locator, self.timeout_ms)

    def _locator(self, locator: str):
        if self._frame:
            return self._frame.locator(locator)
        return self.page.locator(locator)

    def _screenshot_path(self, filename: Optional[str]) -> str:
        base_dir = self.artifacts_dir or os.getcwd()
        screenshots_dir = ensure_dir(os.path.join(base_dir, SCREENSHOTS_DIR_NAME))
        name = filename or f"screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}.png"
        if not name.lower().endswith(".png"):
            name += ".png"
        if os.path.isabs(name):
            return name
        return os.path.join(screenshots_dir, name)

    def _wait_for_enabled_state(self, locator: str, should_be_enabled: bool) -> None:
        self._locator(locator).wait_for(state="visible", timeout=self.timeout_ms)
        end_time = time.monotonic() + (self.timeout_ms / 1000)
        while time.monotonic() < end_time:
            try:
                is_enabled = self._locator(locator).is_enabled()
            except Exception:  # noqa: BLE001
                is_enabled = False
            if is_enabled == should_be_enabled:
                return
            time.sleep(0.1)
        state_label = "enabled" if should_be_enabled else "disabled"
        raise TimeoutError(f"Timed out waiting for element to be {state_label}: {locator}")
