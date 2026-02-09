"""Aggregate keyword libraries for codeless execution."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Optional

import logging

from core.api_client import ApiClient
from keywords.api_keywords import APIKeywords
from keywords.ui_keywords import UIKeywords


@dataclass
class KeywordLibrary:
    """Container for UI and API keyword handlers."""

    ui: UIKeywords
    api: APIKeywords
    flow_handler: Optional[Callable[[str], None]]
    logger: Optional[logging.Logger]

    @staticmethod
    def from_context(
        page,
        api_client: ApiClient,
        timeout_ms: int,
        flow_handler: Optional[Callable[[str], None]] = None,
        logger: Optional[logging.Logger] = None,
        artifacts_dir: Optional[str] = None,
        manager=None,
    ) -> "KeywordLibrary":
        """Create keyword library instances from execution context."""
        return KeywordLibrary(
            ui=UIKeywords(page, timeout_ms, artifacts_dir=artifacts_dir, manager=manager),
            api=APIKeywords(api_client),
            flow_handler=flow_handler,
            logger=logger,
        )

    def call_flow(self, flow_name: str) -> None:
        """Invoke a reusable flow via the assigned handler."""
        if not self.flow_handler:
            raise ValueError("CALL_FLOW is not configured for this execution.")
        if self.logger:
            self.logger.info("[FLOW START] %s", flow_name)
        try:
            self.flow_handler(flow_name)
        finally:
            if self.logger:
                self.logger.info("[FLOW END] %s", flow_name)
