"""Base protocol for project parsers."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from ..models import DbtProject


class ProjectParser(Protocol):
    """Protocol for parsing a data project into the IR."""

    def parse(self, project_dir: Path) -> DbtProject:
        """Parse the project at the given directory and return the IR."""
        ...
