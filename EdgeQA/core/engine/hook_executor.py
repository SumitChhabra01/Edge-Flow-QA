"""Hook executor for before/after steps."""

from __future__ import annotations

from typing import Optional

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.engine.dsl_executor import DslExecutor


class HookExecutor:
    """Execute before/after hooks using the DSL executor."""

    def __init__(self, executor: DslExecutor) -> None:
        self.executor = executor

    def execute_hook(self, hook_sheet: Optional[str], workbook, context=None) -> None:
        """Execute hook steps if present."""
        if not hook_sheet:
            return
        self.executor.execute_steps_sheet(workbook, hook_sheet, context=context)
