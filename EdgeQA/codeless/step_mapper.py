"""Map codeless actions to keyword implementations."""

from __future__ import annotations

from typing import Callable, Dict, Optional

from keywords.api_keywords import APIKeywords
from keywords.ui_keywords import UIKeywords


def build_action_map(ui: UIKeywords, api: APIKeywords, call_flow: Optional[Callable[[str], None]] = None) -> Dict[str, Callable]:
    """Return a mapping from action name to callable."""
    action_map = {
        "open_url": ui.open_url,
        "click": ui.click,
        "double_click": ui.double_click,
        "right_click": ui.right_click,
        "fill_text": ui.fill_text,
        "clear_text": ui.clear_text,
        "press_key": ui.press_key,
        "select_dropdown": ui.select_dropdown,
        "hover": ui.hover,
        "scroll_to": ui.scroll_to,
        "wait_for_element": ui.wait_for_element,
        "wait_for_visible": ui.wait_for_visible,
        "wait_for_hidden": ui.wait_for_hidden,
        "wait_for_attached": ui.wait_for_attached,
        "wait_for_detached": ui.wait_for_detached,
        "wait_for_enabled": ui.wait_for_enabled,
        "wait_for_disabled": ui.wait_for_disabled,
        "wait_for_text": ui.wait_for_text,
        "assert_text": ui.assert_text,
        "assert_contains_text": ui.assert_contains_text,
        "assert_visible": ui.assert_visible,
        "assert_title": ui.assert_title,
        "screenshot_full_page": ui.screenshot_full_page,
        "screenshot_element": ui.screenshot_element,
        "browser_back": ui.browser_back,
        "browser_refresh": ui.browser_refresh,
        "wait_for_url": ui.wait_for_url,
        "wait_for_load_state": ui.wait_for_load_state,
        "new_tab": ui.new_tab,
        "switch_window": ui.switch_window,
        "close_tab": ui.close_tab,
        "launch_incognito_mode": ui.launch_incognito_mode,
        "switch_to_frame": ui.switch_to_frame,
        "switch_to_main_frame": ui.switch_to_main_frame,
        "maximize_window": ui.maximize_window,
        "api_get": api.api_get,
        "api_post": api.api_post,
        "api_put": api.api_put,
        "api_delete": api.api_delete,
        "api_patch": api.api_patch,
        "api_head": api.api_head,
    }
    if call_flow:
        action_map["CALL_FLOW"] = call_flow
    return action_map
