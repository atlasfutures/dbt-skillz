"""Base protocol for skill generators."""

from __future__ import annotations

from pathlib import Path
from typing import Protocol

from ..models import DbtProject


class SkillGenerator(Protocol):
    """Protocol for generating skill files from the project IR."""

    def generate(
        self,
        project: DbtProject,
        output_dir: Path,
        *,
        skill_name: str | None = None,
        include_sql: bool = False,
        max_skill_lines: int = 300,
    ) -> None:
        """Generate skill files from the project IR into output_dir."""
        ...
