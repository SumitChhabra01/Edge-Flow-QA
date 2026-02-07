"""Test generation facade for AI suggestions."""

from __future__ import annotations

from typing import Optional

from ai.ai_engine import AIEngine, NullAIEngine


class TestGenerator:
    """Generate test case suggestions using AI."""

    def __init__(self, ai_engine: Optional[AIEngine] = None) -> None:
        self.ai_engine = ai_engine or NullAIEngine()

    def suggest(self, context: str) -> str:
        """Return test suggestions for the provided context."""
        return self.ai_engine.generate_tests(context)
