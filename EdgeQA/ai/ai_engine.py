"""Pluggable AI engine interfaces."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Protocol


@dataclass
class FailureInsight:
    """Represents failure classification data."""

    category: str
    confidence: float
    suggestion: Optional[str]


class AIEngine(Protocol):
    """Protocol for AI-powered capabilities."""

    def heal_locator(self, locator: str, page_snapshot: str) -> Optional[str]:
        """Return a better locator if possible."""

    def classify_failure(self, error_message: str, step: str) -> FailureInsight:
        """Classify failure with insight."""

    def generate_tests(self, context: str) -> str:
        """Generate test suggestions based on context."""

    def detect_flaky(self, history: str) -> bool:
        """Detect flaky tests based on history."""


class NullAIEngine:
    """Default AI engine with safe, no-op behavior."""

    def heal_locator(self, locator: str, page_snapshot: str) -> Optional[str]:
        return None

    def classify_failure(self, error_message: str, step: str) -> FailureInsight:
        return FailureInsight(category="unknown", confidence=0.0, suggestion=None)

    def generate_tests(self, context: str) -> str:
        return "No AI engine enabled."

    def detect_flaky(self, history: str) -> bool:
        return False
