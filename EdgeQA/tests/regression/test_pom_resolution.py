"""Unit tests for POM locator resolution."""

from __future__ import annotations

from pathlib import Path

import pytest
from openpyxl import Workbook

from codeless.executor import CodelessExecutor


def _create_object_repo(path: Path) -> None:
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "LoginPage"
    sheet.append(["LocatorName", "LocatorType", "LocatorValue"])
    sheet.append(["username", "css", "#username"])
    sheet.append(["loginBtn", "css", "#loginBtn"])
    workbook.save(path)


def test_resolve_locator_success(tmp_path: Path):
    repo_path = tmp_path / "ObjectRepository.xlsx"
    _create_object_repo(repo_path)
    executor = CodelessExecutor(str(tmp_path))
    executor._object_repo_path = str(repo_path)
    executor._object_repo = {
        "LoginPage": {"username": ("css", "#username")},
    }
    resolved = executor._resolve_locator("LoginPage.username")
    assert resolved == "css=#username"


def test_missing_page():
    executor = CodelessExecutor(".")
    executor._object_repo = {}
    with pytest.raises(ValueError, match="Page 'LoginPage' not found in ObjectRepository.xlsx"):
        executor._resolve_locator("LoginPage.username")


def test_missing_locator():
    executor = CodelessExecutor(".")
    executor._object_repo = {"LoginPage": {"username": ("css", "#username")}}
    with pytest.raises(ValueError, match="Locator 'loginBtn' not found in page 'LoginPage'"):
        executor._resolve_locator("LoginPage.loginBtn")
