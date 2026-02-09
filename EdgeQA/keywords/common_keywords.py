"""Common keyword helpers."""

from __future__ import annotations

from typing import Any

from utils.assertion_utils import assert_equal, assert_true


class CommonKeywords:
    """Common keyword library for shared actions."""

    def assert_equals(self, actual: Any, expected: Any) -> None:
        """Assert equality of actual and expected."""
        assert_equal(actual, expected, "Common assert failed")

    def assert_not_equals(self, actual: Any, expected: Any) -> None:
        """Assert that two values are not equal."""
        assert_true(actual != expected, "Common assert not equals failed")

    def assert_contains(self, container: Any, item: Any) -> None:
        """Assert that container contains item."""
        try:
            result = item in container
        except TypeError:
            result = False
        assert_true(result, "Common assert contains failed")
