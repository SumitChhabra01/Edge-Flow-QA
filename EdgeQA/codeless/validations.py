"""Validation utilities for codeless steps."""

from __future__ import annotations

from typing import Iterable


REQUIRED_ACTIONS = {
    "open_url",
    "click",
    "double_click",
    "right_click",
    "fill_text",
    "clear_text",
    "press_key",
    "select_dropdown",
    "hover",
    "scroll_to",
    "wait_for_element",
    "wait_for_visible",
    "wait_for_hidden",
    "wait_for_attached",
    "wait_for_detached",
    "wait_for_enabled",
    "wait_for_disabled",
    "wait_for_text",
    "assert_text",
    "assert_contains_text",
    "assert_visible",
    "assert_title",
    "screenshot_full_page",
    "screenshot_element",
    "browser_back",
    "browser_refresh",
    "wait_for_url",
    "wait_for_load_state",
    "new_tab",
    "switch_window",
    "close_tab",
    "launch_incognito_mode",
    "switch_to_frame",
    "switch_to_main_frame",
    "maximize_window",
    "api_get",
    "api_post",
    "api_put",
    "api_delete",
    "api_patch",
    "api_head",
    "CALL_FLOW",
}


def validate_actions(actions: Iterable[str]) -> None:
    """Validate supported actions."""
    unsupported = [action for action in actions if action not in REQUIRED_ACTIONS]
    if unsupported:
        raise ValueError(f"Unsupported actions: {unsupported}")


def validate_step_fields(action: str, locator: str | None, value: str | None, expected: str | None) -> None:
    """Validate fields based on action type."""
    if action in {
        "click",
        "double_click",
        "right_click",
        "fill_text",
        "clear_text",
        "press_key",
        "select_dropdown",
        "hover",
        "scroll_to",
        "wait_for_element",
        "wait_for_visible",
        "wait_for_hidden",
        "wait_for_attached",
        "wait_for_detached",
        "wait_for_enabled",
        "wait_for_disabled",
        "wait_for_text",
        "assert_text",
        "assert_contains_text",
        "assert_visible",
        "screenshot_element",
        "switch_to_frame",
    }:
        if not locator:
            raise ValueError(f"Locator is required for action: {action}")
    if action in {"fill_text", "select_dropdown", "press_key"} and value is None:
        raise ValueError(f"Value is required for action: {action}")
    if action in {"wait_for_text", "assert_text", "assert_contains_text", "assert_title"} and expected is None and value is None:
        raise ValueError(f"Expected value is required for action: {action}")
    if action in {"wait_for_url", "wait_for_load_state"} and expected is None and value is None:
        raise ValueError(f"Expected value is required for action: {action}")
    if action in {"switch_window"} and value is None and locator is None:
        raise ValueError("switch_window requires a window index in Locator or Value.")
    if action == "CALL_FLOW" and not (locator or value):
        raise ValueError("CALL_FLOW requires a flow name in Locator or Value.")
