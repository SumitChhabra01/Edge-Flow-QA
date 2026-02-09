"""Evaluate DSL conditions before execution."""

from __future__ import annotations

import re
import time
from dataclasses import dataclass
from typing import Optional


@dataclass
class ConditionResult:
    """Condition evaluation result."""

    should_execute: bool
    retry_count: int


class ConditionEvaluator:
    """Evaluate DSL condition expressions."""

    _retry_pattern = re.compile(r"RETRY\((\d+)\)", re.IGNORECASE)

    def __init__(self, timeout_ms: int = 10000) -> None:
        self.timeout_ms = timeout_ms

    def evaluate(self, condition: Optional[str], target_resolved: Optional[str], context) -> ConditionResult:
        """Evaluate condition string and return result."""
        if not condition:
            return ConditionResult(should_execute=True, retry_count=0)

        normalized = condition.strip().upper()
        retry_match = self._retry_pattern.search(normalized)
        retry_count = int(retry_match.group(1)) if retry_match else 0

        if normalized.startswith("IF_EXISTS"):
            exists = self._exists(target_resolved, context)
            return ConditionResult(should_execute=exists, retry_count=retry_count)
        if normalized.startswith("IF_NOT_EXISTS"):
            exists = self._exists(target_resolved, context)
            return ConditionResult(should_execute=not exists, retry_count=retry_count)
        if normalized.startswith("WAIT_UNTIL"):
            self._wait_until(target_resolved, context)
            return ConditionResult(should_execute=True, retry_count=retry_count)

        return ConditionResult(should_execute=True, retry_count=retry_count)

    def _exists(self, target_resolved: Optional[str], context) -> bool:
        page = context.get("page")
        if not page or not target_resolved:
            return False
        try:
            return page.locator(target_resolved).count() > 0
        except Exception:  # noqa: BLE001
            return False

    def _wait_until(self, target_resolved: Optional[str], context) -> None:
        page = context.get("page")
        if not page or not target_resolved:
            return
        end_time = time.monotonic() + (self.timeout_ms / 1000)
        while time.monotonic() < end_time:
            if self._exists(target_resolved, context):
                return
            time.sleep(0.2)
        raise TimeoutError(f"Condition WAIT_UNTIL timed out for target: {target_resolved}")
