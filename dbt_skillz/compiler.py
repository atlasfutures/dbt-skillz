"""Compiler pipeline: parse -> model -> generate."""

from __future__ import annotations

import shutil
from pathlib import Path

import click

from .generators.skill import SkillGenerator
from .parsers.dbt import DbtParser


def compile_dbt_project(
    project_dir: Path,
    output_dir: Path | None = None,
    skill_name: str | None = None,
    include_sql: bool = False,
    max_skill_lines: int = 300,
    extras_dir: Path | None = None,
) -> None:
    """Parse a dbt project and generate Claude Code skills."""
    project_dir = project_dir.resolve()

    # Parse
    click.echo(f"Parsing dbt project at {project_dir} ...")
    parser = DbtParser()
    project = parser.parse(project_dir)

    click.echo(
        f"  Found {project.total_model_count} models, "
        f"{project.total_source_table_count} source tables, "
        f"{len(project.macros)} macros"
    )
    for layer, models in project.models.items():
        click.echo(f"    {layer}: {len(models)} models")

    # Determine output directory
    if output_dir is None:
        output_dir = Path(".dbt_skills") / project.name.replace("_", "-")
    output_dir = output_dir.resolve()

    # Resolve extras files
    extras_files: list[Path] = []
    resolved_extras_dir: Path | None = None
    if extras_dir is not None:
        resolved_extras_dir = extras_dir.resolve()
        extras_files = sorted(resolved_extras_dir.rglob("*.md"))

    # Generate
    click.echo(f"Generating documentation to {output_dir} ...")
    generator = SkillGenerator()
    if extras_files:
        assert resolved_extras_dir is not None
        extras_relative = [f.relative_to(resolved_extras_dir) for f in extras_files]
    else:
        extras_relative = []

    generator.generate(
        project,
        output_dir,
        skill_name=skill_name,
        include_sql=include_sql,
        max_skill_lines=max_skill_lines,
        extras_files=extras_relative,
    )

    # Copy extras into output
    if extras_files:
        assert resolved_extras_dir is not None, (
            "resolved_extras_dir must be set if extras_files is present"
        )
        click.echo(f"  Copying {len(extras_files)} extras from {resolved_extras_dir} ...")
        for src in extras_files:
            rel = src.relative_to(resolved_extras_dir)
            dest = output_dir / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
            click.echo(f"    {rel}")

    # Report output
    files = list(output_dir.rglob("*.md"))
    click.echo(f"  Generated {len(files)} files:")
    for f in sorted(files):
        lines = f.read_text().count("\n")
        click.echo(f"    {f.relative_to(output_dir)} ({lines} lines)")

    click.echo("Done.")
