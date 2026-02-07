"""Common keyword helpers."""

from __future__ import annotations

from typing import Any

from utils.assertion_utils import assert_equal


class CommonKeywords:
    """Common keyword library for shared actions."""

    def assert_equals(self, actual: Any, expected: Any) -> None:
        """Assert equality of actual and expected."""
        assert_equal(actual, expected, "Common assert failed")
