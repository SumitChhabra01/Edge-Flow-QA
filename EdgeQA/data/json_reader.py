"""JSON data reader for codeless tests."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class StepRecord:
    """Represents a single codeless step from JSON."""

    step: str
    action: str
    locator: Optional[str]
    value: Optional[str]
    expected: Optional[str]


def load_steps_from_json(path: str) -> List[StepRecord]:
    """Load steps from a JSON file."""
    with open(path, "r", encoding="utf-8") as handle:
        payload = json.load(handle)

    steps_data = payload.get("steps", [])
    steps: List[StepRecord] = []
    for item in steps_data:
        steps.append(
            StepRecord(
                step=str(item.get("step", "")).strip(),
                action=str(item.get("action", "")).strip(),
                locator=_to_optional(item.get("locator")),
                value=_to_optional(item.get("value")),
                expected=_to_optional(item.get("expected")),
            )
        )
    return steps


def _to_optional(value) -> Optional[str]:
    if value is None:
        return None
    text = str(value).strip()
    return text if text else None
