"""Runtime context store for DSL execution."""

from __future__ import annotations

import re
from typing import Any, Dict, Optional


class ContextStore:
    """Store and resolve runtime variables for DSL execution."""

    _pattern = re.compile(r"\$\{([^}]+)\}")

    def __init__(self, initial: Optional[Dict[str, Any]] = None) -> None:
        self._data: Dict[str, Any] = initial or {}

    def set(self, key: str, value: Any) -> None:
        """Set a context variable."""
        self._data[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """Get a context variable."""
        return self._data.get(key, default)

    def resolve(self, text: Optional[str]) -> Optional[str]:
        """Resolve ${VAR} placeholders in a string."""
        if text is None:
            return None
        if not isinstance(text, str):
            return str(text)

        def _replace(match) -> str:
            name = match.group(1)
            value = self.get(name, "")
            return str(value)

        return self._pattern.sub(_replace, text)

    def to_dict(self) -> Dict[str, Any]:
        """Return a shallow copy of context data."""
        return dict(self._data)
