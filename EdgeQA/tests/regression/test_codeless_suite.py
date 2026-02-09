"""Execute codeless suites via pytest."""

from __future__ import annotations

import os

import pytest

from codeless.executor import CodelessExecutor
from core.constants import ENV_VAR_CODELESS_SUITE

pytest.skip("Legacy codeless engine is deprecated. Use DSL runner.", allow_module_level=True)


@pytest.mark.codeless
@pytest.mark.regression
def test_codeless_suite():
    """Run codeless suite if provided by environment variable."""
    suite_path = os.getenv(ENV_VAR_CODELESS_SUITE)
    if not suite_path:
        pytest.skip(f"{ENV_VAR_CODELESS_SUITE} not set")
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    executor = CodelessExecutor(root_dir)
    executor.execute_suite(suite_path)
