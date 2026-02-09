"""CLI runner for DSL engine (Excel-based)."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from core.constants import ENV_VAR_BROWSER, ENV_VAR_ENV


def main() -> int:
    """Run DSL engine with configurable options."""
    parser = argparse.ArgumentParser(description="Run EdgeQA DSL engine.")
    parser.add_argument("--testcases", required=True, help="Path to TestCases.xlsx")
    parser.add_argument("--environment", default=None, help="Environment name")
    parser.add_argument("--browser", default=None, help="Browser name")
    args = parser.parse_args()

    if args.environment:
        os.environ[ENV_VAR_ENV] = args.environment
    if args.browser:
        os.environ[ENV_VAR_BROWSER] = args.browser
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    runner_path = os.path.join(root_dir, "runner.py")
    return subprocess.call([sys.executable, runner_path, "--testcases", args.testcases])


if __name__ == "__main__":
    raise SystemExit(main())
