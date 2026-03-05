"""CLI entry point for data-skillz."""

from __future__ import annotations

from pathlib import Path

import click


@click.group()
@click.version_option()
def cli() -> None:
    """Auto-generate Markdown documentation from dbt projects."""


@cli.command()
@click.option(
    "--project-dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=".",
    help="dbt project root directory.",
)
@click.option(
    "--output",
    type=click.Path(path_type=Path),
    default=None,
    help="Output documentation directory. Defaults to .dbt_skills/{project_name}.",
)
@click.option(
    "--skill-name",
    type=str,
    default=None,
    help="Override the skill name (default: derived from dbt_project.yml).",
)
@click.option(
    "--include-sql",
    is_flag=True,
    default=False,
    help="Include SQL snippets in reference docs.",
)
@click.option(
    "--max-skill-lines",
    type=int,
    default=300,
    help="Maximum lines for the main SKILL.md file.",
)
@click.option(
    "--extras-dir",
    type=click.Path(exists=True, file_okay=False, path_type=Path),
    default=None,
    help="Directory of static .md files to copy into the output alongside generated content.",
)
def compile(
    project_dir: Path,
    output: Path | None,
    skill_name: str | None,
    include_sql: bool,
    max_skill_lines: int,
    extras_dir: Path | None,
) -> None:
    """Compile a dbt project into hierarchical Markdown documentation."""
    from .compiler import compile_dbt_project

    compile_dbt_project(
        project_dir=project_dir,
        output_dir=output,
        skill_name=skill_name,
        include_sql=include_sql,
        max_skill_lines=max_skill_lines,
        extras_dir=extras_dir,
    )
