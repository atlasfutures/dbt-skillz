"""Pytest configuration and fixtures."""

from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def fixture_project_dir() -> Path:
    """Return path to the basic test fixture dbt project."""
    return Path(__file__).parent / "fixtures" / "basic_project"
