"""CLI runner for API tests."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from core.constants import ENV_VAR_ENV, ENV_VAR_TAGS


def main() -> int:
    """Run API tests with configurable options."""
    parser = argparse.ArgumentParser(description="Run EdgeQA API tests.")
    parser.add_argument("--environment", default=None, help="Environment name")
    parser.add_argument("--tags", default="api", help="Pytest markers to include")
    parser.add_argument("--parallel", type=int, default=0, help="Parallel workers (0=auto)")
    args = parser.parse_args()

    if args.environment:
        os.environ[ENV_VAR_ENV] = args.environment
    if args.tags:
        os.environ[ENV_VAR_TAGS] = args.tags

    pytest_args = ["-m", args.tags, "tests/api"]
    if args.parallel is not None and (args.parallel == 0 or args.parallel > 1):
        workers = "auto" if args.parallel == 0 else str(args.parallel)
        pytest_args.extend(["-n", workers])

    return subprocess.call([sys.executable, "-m", "pytest", *pytest_args])


if __name__ == "__main__":
    raise SystemExit(main())
