"""Validation utilities for codeless steps."""

from __future__ import annotations

from typing import Iterable


REQUIRED_ACTIONS = {
    "open_url",
    "click",
    "fill_text",
    "select_dropdown",
    "hover",
    "wait_for_element",
    "assert_text",
    "assert_visible",
    "api_get",
    "api_post",
    "api_put",
    "api_delete",
    "CALL_FLOW",
}


def validate_actions(actions: Iterable[str]) -> None:
    """Validate supported actions."""
    unsupported = [action for action in actions if action not in REQUIRED_ACTIONS]
    if unsupported:
        raise ValueError(f"Unsupported actions: {unsupported}")


def validate_step_fields(action: str, locator: str | None, value: str | None, expected: str | None) -> None:
    """Validate fields based on action type."""
    if action in {"click", "fill_text", "select_dropdown", "hover", "wait_for_element", "assert_text", "assert_visible"}:
        if not locator:
            raise ValueError(f"Locator is required for action: {action}")
    if action in {"fill_text", "select_dropdown"} and value is None:
        raise ValueError(f"Value is required for action: {action}")
    if action == "CALL_FLOW" and not (locator or value):
        raise ValueError("CALL_FLOW requires a flow name in Locator or Value.")
