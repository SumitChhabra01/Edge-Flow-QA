"""Generate EdgeQA HTML report for DSL engine."""

from __future__ import annotations

import html
import os
import re
import shutil
from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

from utils.file_utils import ensure_dirs, resolve_path


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
    failure_entries: List[dict]


def write_report(root_dir: str, tests: List[TestRecord]) -> str:
    """Write EdgeQA report and return its path."""
    reports_dir = resolve_path(root_dir, "reports")
    human_dir = resolve_path(reports_dir, "human")
    screenshots_dir = resolve_path(reports_dir, "artifacts", "screenshots")
    report_path = resolve_path(reports_dir, EDGEQA_REPORT_NAME)
    ensure_dirs([reports_dir, human_dir, screenshots_dir])

    collected = len(tests)
    failed = len([test for test in tests if test.status == "FAILED"])
    passed = max(collected - failed, 0)
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    all_screenshots = _collect_all_screenshots(screenshots_dir, human_dir)

    html_content = _build_human_report(
        timestamp=timestamp,
        total=collected,
        passed=passed,
        failed=failed,
        tests=tests,
        human_dir=human_dir,
        all_screenshots=all_screenshots,
    )
    with open(report_path, "w", encoding="utf-8") as handle:
        handle.write(html_content)
    return report_path


def clean_screenshots(root_dir: str) -> None:
    """Remove old screenshots before run."""
    screenshots_dir = resolve_path(root_dir, "reports", "artifacts", "screenshots")
    if not os.path.exists(screenshots_dir):
        return
    for name in os.listdir(screenshots_dir):
        item = os.path.join(screenshots_dir, name)
        try:
            if os.path.isfile(item):
                os.remove(item)
            elif os.path.isdir(item):
                shutil.rmtree(item)
        except Exception:  # noqa: BLE001
            continue


def _build_human_report(
    timestamp: str,
    total: int,
    passed: int,
    failed: int,
    tests: List[TestRecord],
    human_dir: str,
    all_screenshots: List[str],
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
        failure_details = _build_failure_entries_html(record.failure_entries)

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
          {failure_details}
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
    screenshots_html = _build_all_screenshots_html(all_screenshots)

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
        .gallery {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: 12px; }}
        .gallery img {{ width: 100%; border: 1px solid #ddd; border-radius: 6px; }}
        .gallery .item {{ background: #fff; padding: 8px; border-radius: 6px; box-shadow: 0 1px 2px rgba(0,0,0,0.06); }}
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
      <h2>All Screenshots</h2>
      {screenshots_html}
    </body>
    </html>
    """


def _extract_root_cause(error_message: str) -> str:
    for line in error_message.splitlines():
        if line.strip():
            return line.strip()
    return "Unknown error"


def _build_steps_html(steps: List[str], failed_step: Optional[str]) -> str:
    if not steps:
        return "<div class='ok'>No steps captured.</div>"
    items = []
    for step in steps:
        css = "failed" if failed_step and failed_step in step else ""
        items.append(f"<li class='{css}'>{html.escape(step)}</li>")
    return f"<ul>{''.join(items)}</ul>"


def _build_failure_entries_html(entries: List[dict]) -> str:
    if not entries:
        return ""
    items = []
    for entry in entries:
        screenshot_html = ""
        if entry.get("screenshot"):
            name = os.path.basename(entry["screenshot"])
            screenshot_html = f"""
            <div class="label">Failure Screenshot</div>
            <img src="human/all_screenshots/{html.escape(name)}" alt="Failure screenshot" />
            """
        items.append(
            f"""
            <div class="log-snippet">
              <strong>Failure ({html.escape(entry.get('category', 'UNKNOWN'))}):</strong>
              <pre>{html.escape(entry.get('step', ''))}\n{html.escape(entry.get('error', ''))}</pre>
              {screenshot_html}
            </div>
            """
        )
    return "".join(items)


def _collect_all_screenshots(screenshots_dir: str, human_dir: str) -> List[str]:
    if not os.path.exists(screenshots_dir):
        return []
    target_dir = resolve_path(human_dir, "all_screenshots")
    ensure_dirs([target_dir])
    paths = []
    for name in sorted(os.listdir(screenshots_dir)):
        if not name.lower().endswith(".png"):
            continue
        source = resolve_path(screenshots_dir, name)
        dest = resolve_path(target_dir, name)
        try:
            shutil.copyfile(source, dest)
            paths.append(dest)
        except Exception:  # noqa: BLE001
            continue
    return paths


def _build_all_screenshots_html(paths: List[str]) -> str:
    if not paths:
        return "<div class='ok'>No screenshots captured.</div>"
    items = []
    for path in paths:
        rel_path = f"human/all_screenshots/{html.escape(os.path.basename(path))}"
        items.append(
            f"""
            <div class="item">
              <div class="label">{html.escape(os.path.basename(path))}</div>
              <img src="{rel_path}" alt="Screenshot" />
            </div>
            """
        )
    return f"<div class='gallery'>{''.join(items)}</div>"


def summarize_error(error_message: str) -> str:
    """Return a concise error summary."""
    lines = [line for line in error_message.splitlines() if line.strip()]
    if not lines:
        return ""
    return "\n".join(lines[-6:])


def safe_name(text: str) -> str:
    """Return a filesystem-safe name."""
    safe = re.sub(r"[^a-zA-Z0-9_.-]+", "_", text)
    return safe.strip("_")
