"""Codeless test executor for Excel and JSON suites."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import asyncio
import contextlib
import threading

try:
    import allure
except Exception:  # noqa: BLE001
    allure = None

from ai.failure_analyzer import FailureAnalyzer
from ai.self_healing import SelfHealingLocator
from codeless.keyword_library import KeywordLibrary
from codeless.step_mapper import build_action_map
from codeless.validations import validate_actions, validate_step_fields
from core.api_client import ApiClient
from core.driver_factory import create_playwright_manager
from data.excel_reader import load_flows_from_excel, load_steps_from_excel, load_testcases_from_excel
from data.json_reader import load_steps_from_json
from data.object_repository_loader import load_object_repository
from utils.config_loader import load_config
from utils.file_utils import ensure_dirs, resolve_path
from utils.logger import get_logger


@dataclass
class CodelessStep:
    """Normalized codeless step."""

    step: str
    action: str
    locator: Optional[str]
    value: Optional[str]
    expected: Optional[str]


class FlowResolver:
    """Resolve reusable flows with safety checks."""

    def __init__(self, flows: Dict[str, List[CodelessStep]], test_case_ids: List[str], max_depth: int = 3) -> None:
        self.flows = flows
        self.test_case_ids = set(test_case_ids)
        self.max_depth = max_depth

    def get_flow(self, flow_name: str, stack: List[str]) -> List[CodelessStep]:
        """Return flow steps with validation."""
        if flow_name in stack:
            chain = " -> ".join(stack + [flow_name])
            raise ValueError(f"Circular flow detected: {chain}")
        if flow_name in self.test_case_ids:
            raise ValueError(f"Flow-to-test call not allowed: {flow_name}")
        if flow_name not in self.flows:
            raise ValueError(f"Missing flow: {flow_name}")
        if len(stack) >= self.max_depth:
            raise ValueError(f"Flow call depth exceeded: {self.max_depth}")
        return self.flows[flow_name]


class CodelessExecutor:
    """Execute codeless suites from Excel or JSON inputs."""

    def __init__(self, root_dir: str) -> None:
        self.root_dir = root_dir
        self.config = load_config(root_dir)
        self.logger = get_logger("edgeqa_codeless", logs_dir=resolve_path(root_dir, "logs"))
        self.failure_analyzer = FailureAnalyzer() if self.config["config"]["ai"]["enabled"] else None
        self.self_healer = SelfHealingLocator() if self.config["config"]["ai"]["enabled"] else None
        self._flow_stack: List[str] = []
        self._flow_resolver: Optional[FlowResolver] = None
        self._suite_dir: Optional[str] = None
        self._object_repo: Dict[str, Dict[str, Tuple[str, str]]] = {}
        self._object_repo_path = resolve_path(self.root_dir, "InputSheet", "ObjectRepository.xlsx")
        self._action_map = None
        self._manager = None

    def execute_suite(self, suite_path: str, sheet_name: Optional[str] = None) -> None:
        """Execute a codeless suite."""
        if _is_event_loop_running():
            _run_in_thread(self._execute_suite_internal, suite_path, sheet_name)
            return
        self._execute_suite_internal(suite_path, sheet_name)

    def _execute_suite_internal(self, suite_path: str, sheet_name: Optional[str]) -> None:
        """Execute a codeless suite in the current thread."""
        self._suite_dir = os.path.dirname(suite_path)
        self._object_repo = load_object_repository(self._object_repo_path)
        steps_by_test, flows, test_case_ids = self._load_steps(suite_path, sheet_name)
        self._flow_resolver = FlowResolver(flows, test_case_ids)
        for steps in steps_by_test.values():
            validate_actions(step.action for step in steps)
        for flow_steps in flows.values():
            validate_actions(step.action for step in flow_steps)

        reports_dir = resolve_path(self.root_dir, "reports")
        artifacts_dir = resolve_path(reports_dir, "artifacts")
        ensure_dirs([reports_dir, artifacts_dir])

        browser_name = self.config["browser_name"]
        browser_config = self.config["browser"]
        env = self.config["environment"]

        record_video = bool(self.config["config"]["video"]["enabled"])
        manager = create_playwright_manager(browser_name, browser_config, artifacts_dir, record_video=record_video)
        page = manager.start()

        api_client = ApiClient(
            base_url=env.get("api_base_url", ""),
            timeout_ms=self.config["config"]["timeouts"]["api"],
            playwright=manager.playwright,
        )
        api_client.start()

        keywords = KeywordLibrary.from_context(
            page=page,
            api_client=api_client,
            timeout_ms=self.config["config"]["timeouts"]["default"],
            flow_handler=self._execute_flow,
            logger=self.logger,
            artifacts_dir=artifacts_dir,
            manager=manager,
        )
        action_map = build_action_map(keywords.ui, keywords.api, call_flow=keywords.call_flow)
        self._set_execution_context(action_map, manager)

        try:
            for test_name, steps in steps_by_test.items():
                self.logger.info("Starting codeless test: %s", test_name)
                for step in steps:
                    self._execute_step(step, action_map, manager)
        finally:
            api_client.stop()
            manager.stop()

    def _execute_step(self, step: CodelessStep, action_map, manager, flow_name: Optional[str] = None) -> None:
        """Execute a single codeless step with retry and logging."""
        retries = int(self.config["config"]["retries"]["step"])
        attempt = 0
        while True:
            try:
                validate_step_fields(step.action, step.locator, step.value, step.expected)
                if flow_name:
                    self.logger.info("[FLOW STEP] %s -> %s", step.action, step.locator or step.value or "")
                else:
                    self.logger.info("Executing step: %s | action=%s", step.step, step.action)
                step_title = _build_step_title(step, flow_name)
                with _allure_step(step_title):
                    self._dispatch(step, action_map)
                return
            except Exception as exc:  # noqa: BLE001
                attempt += 1
                if self.self_healer and step.locator:
                    try:
                        page_snapshot = manager.page.content() if manager.page else ""
                        healed = self.self_healer.heal(step.locator, page_snapshot)
                        if healed:
                            self.logger.info("Self-healed locator for step %s: %s", step.step, healed)
                            step.locator = healed
                    except Exception:  # noqa: BLE001
                        pass
                screenshot = manager.screenshot_on_failure(step.step)
                self.logger.error("Step failed: %s | error=%s | screenshot=%s", step.step, str(exc), screenshot)
                if self.failure_analyzer:
                    insight = self.failure_analyzer.analyze(str(exc), step.step)
                    self.logger.error("Failure insight: %s", insight)
                if attempt > retries:
                    raise

    def _dispatch(self, step: CodelessStep, action_map) -> None:
        """Dispatch a step to its corresponding action."""
        action = action_map[step.action]
        if step.action == "open_url":
            base_url = self.config["environment"].get("base_url", "")
            url = step.value or step.locator or ""
            action(_combine_url(base_url, self._resolve_placeholders(url)))
            return
        if step.action == "CALL_FLOW":
            flow_name = self._resolve_placeholders(step.locator or step.value or "")
            action(flow_name)
            return
        if step.action in {
            "click",
            "double_click",
            "right_click",
            "hover",
            "scroll_to",
            "wait_for_element",
            "wait_for_visible",
            "wait_for_hidden",
            "wait_for_attached",
            "wait_for_detached",
            "wait_for_enabled",
            "wait_for_disabled",
            "assert_visible",
            "clear_text",
            "browser_back",
            "browser_refresh",
            "launch_incognito_mode",
            "switch_to_main_frame",
            "maximize_window",
        }:
            if step.action in {
                "browser_back",
                "browser_refresh",
                "launch_incognito_mode",
                "switch_to_main_frame",
                "maximize_window",
            }:
                action()
            else:
                action(self._resolve_locator(self._resolve_placeholders(step.locator or "")))
            return
        if step.action in {"fill_text", "select_dropdown", "press_key"}:
            action(
                self._resolve_locator(self._resolve_placeholders(step.locator or "")),
                self._resolve_placeholders(step.value or ""),
            )
            return
        if step.action == "screenshot_full_page":
            action(self._resolve_placeholders(step.value or step.expected))
            return
        if step.action == "screenshot_element":
            action(
                self._resolve_locator(self._resolve_placeholders(step.locator or "")),
                self._resolve_placeholders(step.value or step.expected),
            )
            return
        if step.action == "new_tab":
            action(self._resolve_placeholders(step.value or step.locator))
            return
        if step.action == "switch_window":
            action(_to_int(self._resolve_placeholders(step.value or step.locator) or "0") or 0)
            return
        if step.action == "close_tab":
            index = _to_int(self._resolve_placeholders(step.value or step.locator))
            action(index)
            return
        if step.action == "switch_to_frame":
            action(self._resolve_locator(self._resolve_placeholders(step.locator or "")))
            return
        if step.action in {"assert_text", "assert_contains_text"}:
            action(
                self._resolve_locator(self._resolve_placeholders(step.locator or "")),
                self._resolve_placeholders(step.expected or step.value or ""),
            )
            return
        if step.action == "wait_for_text":
            action(
                self._resolve_locator(self._resolve_placeholders(step.locator or "")),
                self._resolve_placeholders(step.expected or step.value or ""),
            )
            return
        if step.action == "assert_title":
            action(self._resolve_placeholders(step.expected or step.value or ""))
            return
        if step.action == "wait_for_url":
            action(self._resolve_placeholders(step.expected or step.value or ""))
            return
        if step.action == "wait_for_load_state":
            action(self._resolve_placeholders(step.expected or step.value or ""))
            return
        if step.action in {"api_get", "api_head"}:
            endpoint = step.value or step.locator or ""
            action(self._resolve_placeholders(endpoint), expected_status=_to_int(self._resolve_placeholders(step.expected)))
            return
        if step.action in {"api_post", "api_put", "api_delete", "api_patch"}:
            payload = self._load_payload(step.value)
            action(self._resolve_placeholders(step.locator or ""), payload, expected_status=_to_int(self._resolve_placeholders(step.expected)))
            return
        raise ValueError(f"Unsupported action: {step.action}")

    def _load_steps(
        self,
        suite_path: str,
        sheet_name: Optional[str],
    ) -> tuple[Dict[str, List[CodelessStep]], Dict[str, List[CodelessStep]], List[str]]:
        """Load suite steps and flows from Excel or JSON."""
        if suite_path.endswith(".xlsx"):
            flows = _normalize_records(load_flows_from_excel(suite_path))
            testcases = load_testcases_from_excel(suite_path)
            test_case_ids = [case.test_case_id for case in testcases]
            if sheet_name:
                records = load_steps_from_excel(suite_path, sheet_name=sheet_name)
                return {"sheet": _records_to_steps(records)}, flows, test_case_ids
            if testcases:
                steps_by_test = {}
                for case in testcases:
                    if case.execute:
                        records = load_steps_from_excel(suite_path, sheet_name=case.test_case_id)
                        steps_by_test[case.test_case_id] = _records_to_steps(records)
                return steps_by_test, flows, test_case_ids
            records = load_steps_from_excel(suite_path, sheet_name=None)
            return {"sheet": _records_to_steps(records)}, flows, test_case_ids
        elif suite_path.endswith(".json"):
            records = load_steps_from_json(suite_path)
            return {"sheet": _records_to_steps(records)}, {}, []
        else:
            raise ValueError("Unsupported suite file. Use .xlsx or .json")

    def _execute_flow(self, flow_name: str) -> None:
        """Execute a reusable flow with safety checks."""
        if not self._flow_resolver:
            raise ValueError("Flow resolver not initialized.")
        if not flow_name:
            raise ValueError("CALL_FLOW requires a flow name.")
        flow_steps = self._flow_resolver.get_flow(flow_name, self._flow_stack)
        self._flow_stack.append(flow_name)
        try:
            with _allure_step(f"[FLOW START] {flow_name}"):
                for step in flow_steps:
                    self._execute_step(step, self._action_map, self._manager, flow_name=flow_name)
        finally:
            self._flow_stack.pop()

    def _resolve_placeholders(self, text: Optional[str]) -> Optional[str]:
        """Resolve placeholders using configured context."""
        if text is None:
            return None
        resolved = text
        variables = self._build_variable_context()
        for key, value in variables.items():
            resolved = resolved.replace(f"{{{{{key}}}}}", value)
        return resolved

    def _build_variable_context(self) -> Dict[str, str]:
        """Build a dictionary of placeholder variables."""
        context = {
            "base_url": self.config["environment"].get("base_url", ""),
            "api_base_url": self.config["environment"].get("api_base_url", ""),
        }
        for key, value in os.environ.items():
            if key.startswith("EDGEQA_VAR_"):
                context[key.replace("EDGEQA_VAR_", "").lower()] = value
        return context

    def _load_payload(self, value: Optional[str]) -> Dict[str, object]:
        """Load API payload from inline JSON or a file."""
        if not value:
            return {}
        resolved = self._resolve_placeholders(value) or ""
        if resolved.endswith(".json") and self._suite_dir:
            payload_path = os.path.join(self._suite_dir, resolved)
            if os.path.exists(payload_path):
                with open(payload_path, "r", encoding="utf-8") as handle:
                    return json.load(handle)
        return json.loads(resolved)

    def _set_execution_context(self, action_map, manager) -> None:
        """Store execution context for nested flow calls."""
        self._action_map = action_map
        self._manager = manager

    def _resolve_locator(self, locator: Optional[str]) -> str:
        """Resolve POM-style locators to Playwright selectors."""
        if locator is None:
            return ""
        if "." not in locator:
            return locator
        if locator.count(".") != 1:
            raise ValueError("Invalid locator format. Expected PageName.LocatorName")
        page_name, locator_name = locator.split(".", 1)
        if not page_name or not locator_name:
            raise ValueError("Invalid locator format. Expected PageName.LocatorName")
        if page_name not in self._object_repo:
            raise ValueError(f"Page '{page_name}' not found in ObjectRepository.xlsx")
        page_locators = self._object_repo.get(page_name, {})
        if locator_name not in page_locators:
            raise ValueError(f"Locator '{locator_name}' not found in page '{page_name}'")
        locator_type, locator_value = page_locators[locator_name]
        selector = _to_selector(locator_type, locator_value)
        self.logger.info("[POM] Resolved %s -> %s", locator, selector)
        _allure_attach_text(f"{locator} -> {selector}", "POM Resolver")
        return selector


def _combine_url(base_url: str, path: str) -> str:
    if path.startswith("http://") or path.startswith("https://"):
        return path
    if base_url.endswith("/") and path.startswith("/"):
        return base_url[:-1] + path
    if not base_url.endswith("/") and not path.startswith("/"):
        return f"{base_url}/{path}"
    return base_url + path


def _to_int(value: Optional[str]) -> Optional[int]:
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def _records_to_steps(records: List[object]) -> List[CodelessStep]:
    """Convert Excel/JSON step records to CodelessStep objects."""
    return [CodelessStep(**record.__dict__) for record in records]


def _normalize_records(flow_records: Dict[str, List[object]]) -> Dict[str, List[CodelessStep]]:
    """Normalize flow records into CodelessStep lists."""
    return {flow_name: _records_to_steps(records) for flow_name, records in flow_records.items()}


def _build_step_title(step: CodelessStep, flow_name: Optional[str]) -> str:
    """Build a human-readable Allure step title."""
    if flow_name:
        target = step.locator or step.value or ""
        return f"[FLOW STEP] {step.action} -> {target}"
    return f"[STEP] {step.step} | {step.action}"


@contextlib.contextmanager
def _allure_step(title: str):
    """Create a safe Allure step context."""
    if allure:
        with allure.step(title):
            yield
    else:
        yield


def _allure_attach_text(content: str, name: str) -> None:
    if allure:
        try:
            allure.attach(content, name=name, attachment_type=allure.attachment_type.TEXT)
        except Exception:  # noqa: BLE001
            return


def _is_event_loop_running() -> bool:
    """Return True if an asyncio loop is running in this thread."""
    try:
        loop = asyncio.get_running_loop()
        return loop.is_running()
    except RuntimeError:
        return False


def _run_in_thread(func, *args, **kwargs) -> None:
    """Run a callable in a dedicated thread and re-raise errors."""
    exception_holder = []

    def _target():
        try:
            func(*args, **kwargs)
        except Exception as exc:  # noqa: BLE001
            exception_holder.append(exc)

    thread = threading.Thread(target=_target, daemon=True)
    thread.start()
    thread.join()
    if exception_holder:
        raise exception_holder[0]


def _to_selector(locator_type: str, locator_value: str) -> str:
    locator_type = locator_type.strip().lower()
    locator_value = locator_value.strip()
    if locator_value.startswith(("css=", "xpath=", "text=", "id=")):
        return locator_value
    mapping = {
        "css": "css=",
        "xpath": "xpath=",
        "text": "text=",
        "id": "id=",
    }
    prefix = mapping.get(locator_type)
    if not prefix:
        raise ValueError(f"Unsupported locator type: {locator_type}")
    return f"{prefix}{locator_value}"
