"""Resolve Page.Name into Playwright selectors."""

from __future__ import annotations

from typing import Dict, Tuple

from core.locator.locator_loader import LocatorRepo


class LocatorResolver:
    """Resolve semantic locators with primary/secondary fallback."""

    def __init__(self, repository: LocatorRepo) -> None:
        self.repository = repository

    def resolve(self, target: str) -> str:
        """Resolve a locator in Page.Name format."""
        if "." not in target or target.count(".") != 1:
            raise ValueError("Invalid locator format. Expected PageName.LocatorName")
        page, name = target.split(".", 1)
        if page not in self.repository:
            raise ValueError(f"LocatorNotFoundException: {target}")
        if name not in self.repository[page]:
            raise ValueError(f"LocatorNotFoundException: {target}")
        primary, secondary, loc_type, _page = self.repository[page][name]
        selector = _to_selector(loc_type, primary)
        if selector:
            return selector
        if secondary:
            return _to_selector(loc_type, secondary)
        raise ValueError(f"LocatorNotFoundException: {target}")


def _to_selector(loc_type: str, value: str) -> str:
    loc_type = loc_type.strip().lower()
    value = value.strip()
    if value.startswith(("css=", "xpath=", "text=", "id=")):
        return value
    mapping = {
        "css": "css=",
        "xpath": "xpath=",
        "text": "text=",
        "id": "id=",
        "button": "css=",
    }
    prefix = mapping.get(loc_type)
    if not prefix:
        return ""
    return f"{prefix}{value}"
