"""Assertion helpers with clear messages."""

from __future__ import annotations


def assert_equal(actual: object, expected: object, message: str) -> None:
    """Assert equality with a custom message."""
    if actual != expected:
        raise AssertionError(f"{message}. Expected={expected}, Actual={actual}")


def assert_true(condition: bool, message: str) -> None:
    """Assert condition with a custom message."""
    if not condition:
        raise AssertionError(message)
