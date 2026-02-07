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
        "fill_text": ui.fill_text,
        "select_dropdown": ui.select_dropdown,
        "hover": ui.hover,
        "wait_for_element": ui.wait_for_element,
        "assert_text": ui.assert_text,
        "assert_visible": ui.assert_visible,
        "api_get": api.api_get,
        "api_post": api.api_post,
        "api_put": api.api_put,
        "api_delete": api.api_delete,
    }
    if call_flow:
        action_map["CALL_FLOW"] = call_flow
    return action_map
