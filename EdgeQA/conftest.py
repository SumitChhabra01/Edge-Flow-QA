"""Pytest configuration for EdgeQA."""

from __future__ import annotations

import html
import os
import re
import shutil
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import pytest

from utils.file_utils import ensure_dirs, resolve_path

pytest_plugins = ["core.base_test"]

EDGEQA_REPORT_NAME = "edgeqa_report.html"


@dataclass
class TestRecord:
    """Represents a test case with reporting details."""

    nodeid: str
    test_name: str
    status: str
    root_cause: Optional[str]
    failed_step: Optional[str]
    steps: List[str]
    stderr: str
    error_snippet: str
    screenshot_path: Optional[str]


@pytest.hookimpl(tryfirst=True)
def pytest_configure() -> None:
    """Ensure report and log directories exist before tests run."""
    root_dir = os.path.abspath(os.path.dirname(__file__))
    reports_dir = resolve_path(root_dir, "reports")
    human_dir = resolve_path(reports_dir, "human")
    logs_dir = resolve_path(root_dir, "logs")
    ensure_dirs([reports_dir, human_dir, logs_dir])
    if not hasattr(pytest, "edgeqa_tests"):
        pytest.edgeqa_tests = {}


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Capture test results with screenshots, steps, and root cause."""
    outcome = yield
    report = outcome.get_result()
    if report.when != "call":
        return

    root_dir = os.path.abspath(os.path.dirname(__file__))
    reports_dir = resolve_path(root_dir, "reports")
    human_dir = resolve_path(reports_dir, "human")

    stderr_text = _extract_captured_text(report.sections, "Captured stderr call")
    log_text = _extract_captured_text(report.sections, "Captured log call")
    combined_text = "\n".join([stderr_text, log_text]).strip()
    steps = _extract_steps(combined_text)
    failed_step = _extract_failed_step(combined_text)

    screenshot_path = None
    if report.failed:
        if "page" in item.funcargs:
            page = item.funcargs["page"]
            filename = _safe_filename(report.nodeid) + ".png"
            screenshot_path = resolve_path(human_dir, filename)
            try:
                page.screenshot(path=screenshot_path, full_page=True)
            except Exception:  # noqa: BLE001
                screenshot_path = None
        else:
            screenshot_path = _extract_screenshot_path(report.longreprtext)
            if screenshot_path:
                screenshot_path = _copy_screenshot(screenshot_path, human_dir)

    root_cause = _extract_root_cause(report.longreprtext) if report.failed else None
    error_snippet = _simplify_error_log(combined_text)

    pytest.edgeqa_tests[report.nodeid] = TestRecord(
        nodeid=report.nodeid,
        test_name=item.name,
        status="FAILED" if report.failed else "PASSED",
        root_cause=root_cause,
        failed_step=failed_step,
        steps=steps,
        stderr=combined_text,
        error_snippet=error_snippet,
        screenshot_path=screenshot_path,
    )


def pytest_sessionfinish(session, exitstatus) -> None:
    """Generate a human-friendly HTML report for non-technical users."""
    root_dir = os.path.abspath(os.path.dirname(__file__))
    reports_dir = resolve_path(root_dir, "reports")
    human_dir = resolve_path(reports_dir, "human")
    report_path = resolve_path(reports_dir, EDGEQA_REPORT_NAME)

    tests: Dict[str, TestRecord] = getattr(pytest, "edgeqa_tests", {})
    collected = getattr(session, "testscollected", 0)
    failed = len([test for test in tests.values() if test.status == "FAILED"])
    passed = max(collected - failed, 0)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    html_content = _build_human_report(
        timestamp=timestamp,
        total=collected,
        passed=passed,
        failed=failed,
        tests=list(tests.values()),
        human_dir=human_dir,
    )
    with open(report_path, "w", encoding="utf-8") as handle:
        handle.write(html_content)


def _build_human_report(
    timestamp: str,
    total: int,
    passed: int,
    failed: int,
    tests: List[TestRecord],
    human_dir: str,
) -> str:
    summary = f"""
    <div class="summary">
      <div><strong>Total:</strong> {total}</div>
      <div><strong>Passed:</strong> {passed}</div>
      <div><strong>Failed:</strong> {failed}</div>
      <div><strong>Generated:</strong> {timestamp}</div>
    </div>
    """

    failure_cards = []
    passed_cards = []
    for record in tests:
        screenshot_block = ""
        if record.screenshot_path and os.path.exists(record.screenshot_path):
            rel_path = os.path.relpath(record.screenshot_path, human_dir)
            screenshot_block = f"""
            <div class="screenshot">
              <div class="label">Screenshot</div>
              <img src="human/{html.escape(rel_path)}" alt="Failure screenshot" />
            </div>
            """
        steps_html = _build_steps_html(record.steps, record.failed_step)
        error_section = ""
        if record.status == "FAILED":
            error_section = f"""
            <div class="cause"><strong>Root Cause:</strong> {html.escape(record.root_cause or 'Unknown error')}</div>
            <div class="cause"><strong>Failed Step:</strong> {html.escape(record.failed_step or 'Unknown step')}</div>
            <div class="log-snippet"><strong>Error Log:</strong><pre>{html.escape(record.error_snippet)}</pre></div>
            """

        stderr_section = ""
        if record.stderr:
            stderr_section = f"""
            <div class="log-snippet"><strong>Captured stderr call:</strong><pre>{html.escape(record.stderr)}</pre></div>
            """

        card_html = f"""
        <div class="card {'failed' if record.status == 'FAILED' else 'passed'}">
          <div class="title">{html.escape(record.test_name)} <span class="badge {record.status.lower()}">{record.status}</span></div>
          <div class="nodeid">{html.escape(record.nodeid)}</div>
          {error_section}
          <div class="steps">
            <strong>Steps:</strong>
            {steps_html}
          </div>
          {stderr_section}
          {screenshot_block}
        </div>
        """
        if record.status == "FAILED":
            failure_cards.append(card_html)
        else:
            passed_cards.append(card_html)

    failures_html = "\n".join(failure_cards) if failure_cards else "<div class='ok'>No failures.</div>"
    passed_html = "\n".join(passed_cards) if passed_cards else "<div class='ok'>No passed tests recorded.</div>"

    return f"""
    <!doctype html>
    <html>
    <head>
      <meta charset="utf-8">
      <title>EdgeQA Report</title>
      <style>
        body {{ font-family: Arial, sans-serif; padding: 20px; background: #f6f7f9; }}
        h1 {{ margin-bottom: 8px; }}
        .summary {{ display: grid; grid-template-columns: repeat(4, auto); gap: 16px; margin-bottom: 20px; }}
        .card {{ background: #fff; border-radius: 8px; padding: 16px; margin-bottom: 16px; box-shadow: 0 1px 2px rgba(0,0,0,0.08); }}
        .card.failed {{ border-left: 4px solid #d9534f; }}
        .card.passed {{ border-left: 4px solid #5cb85c; }}
        .title {{ font-size: 16px; font-weight: bold; margin-bottom: 6px; }}
        .nodeid {{ font-size: 12px; color: #666; margin-bottom: 8px; }}
        .cause {{ margin-bottom: 10px; }}
        .steps ul {{ margin: 8px 0 0 18px; }}
        .steps li.failed {{ color: #d9534f; font-weight: bold; }}
        .log-snippet pre {{ background: #f3f4f6; padding: 10px; border-radius: 6px; overflow-x: auto; }}
        .badge {{ font-size: 11px; padding: 2px 6px; border-radius: 4px; color: #fff; margin-left: 6px; }}
        .badge.passed {{ background: #5cb85c; }}
        .badge.failed {{ background: #d9534f; }}
        .screenshot img {{ max-width: 100%; border: 1px solid #ddd; border-radius: 6px; }}
        .label {{ font-size: 12px; color: #444; margin-bottom: 6px; }}
        .ok {{ background: #e7f6ea; padding: 12px; border-radius: 6px; }}
      </style>
    </head>
    <body>
      <h1>EdgeQA Report</h1>
      {summary}
      <h2>Failed Tests</h2>
      {failures_html}
      <h2>Passed Tests</h2>
      {passed_html}
    </body>
    </html>
    """


def _extract_root_cause(longreprtext: str) -> str:
    for line in longreprtext.splitlines():
        if line.startswith("E "):
            return line[2:].strip()
    for line in reversed(longreprtext.splitlines()):
        if line.strip():
            return line.strip()
    return "Unknown error"


def _extract_screenshot_path(text: str) -> Optional[str]:
    match = re.search(r"screenshot=([A-Za-z]:\\\\[^\\s]+\\.png)", text)
    if match:
        return match.group(1)
    match = re.search(r"screenshot=([^\\s]+\\.png)", text)
    if match:
        return match.group(1)
    return None


def _copy_screenshot(path: str, human_dir: str) -> Optional[str]:
    if not os.path.exists(path):
        return None
    ensure_dirs([human_dir])
    dest = resolve_path(human_dir, os.path.basename(path))
    try:
        shutil.copyfile(path, dest)
        return dest
    except Exception:  # noqa: BLE001
        return None


def _safe_filename(text: str) -> str:
    safe = re.sub(r"[^a-zA-Z0-9_.-]+", "_", text)
    return safe.strip("_")


def _extract_captured_text(sections: List[Tuple[str, str]], label: str) -> str:
    for name, content in sections:
        if name == label:
            return content
    return ""


def _extract_steps(text: str) -> List[str]:
    steps = []
    for line in text.splitlines():
        if "Executing step:" in line:
            steps.append(line.split("Executing step:", 1)[1].strip())
        elif "[FLOW STEP]" in line:
            steps.append(line.split("[FLOW STEP]", 1)[1].strip())
    return steps


def _extract_failed_step(text: str) -> Optional[str]:
    failed_line = None
    for line in text.splitlines():
        if "Step failed:" in line:
            failed_line = line
    if failed_line:
        match = re.search(r"Step failed:\s*(.+?)\s*\|\s*error", failed_line)
        if match:
            return match.group(1).strip()
    return steps[-1] if (steps := _extract_steps(text)) else None


def _simplify_error_log(text: str) -> str:
    lines = [line for line in text.splitlines() if "ERROR" in line or "Error:" in line]
    if lines:
        return "\n".join(lines[-6:])
    return "\n".join(text.splitlines()[-6:])


def _build_steps_html(steps: List[str], failed_step: Optional[str]) -> str:
    if not steps:
        return "<div class='ok'>No steps captured.</div>"
    items = []
    for step in steps:
        css = "failed" if failed_step and failed_step in step else ""
        items.append(f"<li class='{css}'>{html.escape(step)}</li>")
    return f"<ul>{''.join(items)}</ul>"
