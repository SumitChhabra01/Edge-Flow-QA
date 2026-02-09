"""CLI runner for DSL engine."""

from __future__ import annotations

import argparse
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from core.engine.dsl_executor import DslExecutor  # noqa: E402


def main() -> int:
    """Run the Excel DSL engine."""
    parser = argparse.ArgumentParser(description="Run EdgeQA Excel DSL engine.")
    parser.add_argument("--testcases", required=True, help="Path to TestCases.xlsx")
    parser.add_argument("--locator-repo", default=None, help="Path to LocatorRepository.xlsx")
    parser.add_argument("--flows-dir", default=None, help="Path to flows directory")
    args = parser.parse_args()

    root_dir = os.path.abspath(os.path.dirname(__file__))
    executor = DslExecutor(
        root_dir=root_dir,
        locator_repo_path=args.locator_repo,
        flows_dir=args.flows_dir,
    )
    executor.execute(args.testcases)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
