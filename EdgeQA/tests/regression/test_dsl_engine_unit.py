"""Unit tests for DSL engine components."""

from __future__ import annotations

from pathlib import Path

import pytest
from openpyxl import Workbook

from core.conditions.condition_evaluator import ConditionEvaluator
from core.engine.context_store import ContextStore
from core.locator.locator_loader import load_locator_repository
from core.locator.locator_resolver import LocatorResolver


class FakeLocator:
    def __init__(self, exists: bool) -> None:
        self._exists = exists

    def count(self) -> int:
        return 1 if self._exists else 0


class FakePage:
    def __init__(self, exists: bool) -> None:
        self._exists = exists

    def locator(self, _selector: str):
        return FakeLocator(self._exists)


def _create_locator_repo(path: Path) -> None:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "LocatorRepository"
    sheet.append(["Page", "Name", "Primary", "Secondary", "Type"])
    sheet.append(["LoginPage", "submit", "#loginBtn", "//button[text()='Login']", "button"])
    workbook.save(path)


def test_locator_resolution_primary(tmp_path: Path):
    repo_path = tmp_path / "LocatorRepository.xlsx"
    _create_locator_repo(repo_path)
    repo = load_locator_repository(str(repo_path))
    resolver = LocatorResolver(repo)
    selector = resolver.resolve("LoginPage.submit")
    assert selector == "css=#loginBtn"


def test_locator_missing_page():
    resolver = LocatorResolver({})
    with pytest.raises(ValueError, match="LocatorNotFoundException:"):
        resolver.resolve("LoginPage.submit")


def test_context_store_resolve():
    context = ContextStore({"policyNumber": "PN123"})
    resolved = context.resolve("Policy ${policyNumber}")
    assert resolved == "Policy PN123"


def test_condition_if_exists_true():
    evaluator = ConditionEvaluator(timeout_ms=100)
    context = ContextStore({"page": FakePage(True)})
    result = evaluator.evaluate("IF_EXISTS", "css=#loginBtn", context)
    assert result.should_execute is True


def test_condition_if_not_exists_true():
    evaluator = ConditionEvaluator(timeout_ms=100)
    context = ContextStore({"page": FakePage(False)})
    result = evaluator.evaluate("IF_NOT_EXISTS", "css=#loginBtn", context)
    assert result.should_execute is True
