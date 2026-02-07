"""Failure analysis and flaky detection."""

from __future__ import annotations

from typing import Optional

from ai.ai_engine import AIEngine, FailureInsight, NullAIEngine


class FailureAnalyzer:
    """Analyze failures and detect flaky behavior."""

    def __init__(self, ai_engine: Optional[AIEngine] = None) -> None:
        self.ai_engine = ai_engine or NullAIEngine()

    def analyze(self, error_message: str, step: str) -> FailureInsight:
        """Classify a failure and suggest remediation."""
        return self.ai_engine.classify_failure(error_message, step)

    def is_flaky(self, history: str) -> bool:
        """Detect flaky tests based on history data."""
        return self.ai_engine.detect_flaky(history)
