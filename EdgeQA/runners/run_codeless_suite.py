"""CLI runner for codeless suites."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from core.constants import ENV_VAR_BROWSER, ENV_VAR_CODELESS_SUITE, ENV_VAR_ENV, ENV_VAR_TAGS


def main() -> int:
    """Run codeless suite with configurable options."""
    parser = argparse.ArgumentParser(description="Run EdgeQA codeless suite.")
    parser.add_argument("--suite", required=True, help="Path to .xlsx or .json suite")
    parser.add_argument("--environment", default=None, help="Environment name")
    parser.add_argument("--browser", default=None, help="Browser name")
    parser.add_argument("--tags", default="codeless", help="Pytest markers to include")
    parser.add_argument("--parallel", type=int, default=1, help="Parallel workers")
    args = parser.parse_args()

    os.environ[ENV_VAR_CODELESS_SUITE] = args.suite
    if args.environment:
        os.environ[ENV_VAR_ENV] = args.environment
    if args.browser:
        os.environ[ENV_VAR_BROWSER] = args.browser
    if args.tags:
        os.environ[ENV_VAR_TAGS] = args.tags

    pytest_args = ["-m", args.tags, "tests/regression"]
    if args.parallel is not None and (args.parallel == 0 or args.parallel > 1):
        workers = "auto" if args.parallel == 0 else str(args.parallel)
        pytest_args.extend(["-n", workers])

    result = subprocess.run([sys.executable, "-m", "pytest", *pytest_args], text=True, capture_output=True)
    if result.stdout:
        print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)

    if result.returncode == 0:
        return 0

    combined_output = f"{result.stdout}\n{result.stderr}"
    if "Playwright Sync API inside the asyncio loop" in combined_output:
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        direct_cmd = (
            "import os; "
            "from codeless.executor import CodelessExecutor; "
            "root=os.getcwd(); "
            f"CodelessExecutor(root).execute_suite(r'{args.suite}')"
        )
        direct_result = subprocess.run([sys.executable, "-c", direct_cmd], cwd=root_dir)
        return direct_result.returncode

    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
