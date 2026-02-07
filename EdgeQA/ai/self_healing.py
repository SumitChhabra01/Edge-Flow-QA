"""Self-healing locator logic."""

from __future__ import annotations

from typing import Optional

from ai.ai_engine import AIEngine, NullAIEngine


class SelfHealingLocator:
    """Resolve alternative locators using AI when enabled."""

    def __init__(self, ai_engine: Optional[AIEngine] = None) -> None:
        self.ai_engine = ai_engine or NullAIEngine()

    def heal(self, locator: str, page_snapshot: str) -> Optional[str]:
        """Try to heal a locator based on a page snapshot."""
        return self.ai_engine.heal_locator(locator, page_snapshot)
