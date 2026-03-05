"""Tests for the CLI."""

from __future__ import annotations

import tempfile
from pathlib import Path

from click.testing import CliRunner

from dbt_skillz.cli import cli


def test_cli_compile_basic(fixture_project_dir: Path) -> None:
    """Test basic CLI compile command."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir) / "output"
        result = runner.invoke(
            cli,
            ["compile", "--project-dir", str(fixture_project_dir), "--output", str(output_dir)],
        )

        # Check exit code
        assert result.exit_code == 0, f"CLI failed with: {result.output}"

        # Check that output was created
        assert output_dir.exists()
        assert (output_dir / "SKILL.md").exists()
        assert (output_dir / "ref" / "sources.md").exists()


def test_cli_compile_with_default_output(fixture_project_dir: Path) -> None:
    """Test CLI compile without specifying output (uses default)."""
    runner = CliRunner()

    with tempfile.TemporaryDirectory() as tmpdir:
        # Change to temp directory to avoid polluting project
        import os

        old_cwd = os.getcwd()
        try:
            os.chdir(tmpdir)
            result = runner.invoke(cli, ["compile", "--project-dir", str(fixture_project_dir)])

            # Check exit code
            assert result.exit_code == 0, f"CLI failed with: {result.output}"

            # Check that default output directory was created
            assert Path(".dbt_skills").exists()
        finally:
            os.chdir(old_cwd)


def test_cli_compile_missing_project(tmp_path: Path) -> None:
    """Test CLI with non-existent project directory."""
    runner = CliRunner()

    result = runner.invoke(
        cli,
        ["compile", "--project-dir", str(tmp_path / "nonexistent")],
    )

    # Should fail with non-zero exit code
    assert result.exit_code != 0


def test_cli_version() -> None:
    """Test CLI version command."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--version"])

    assert result.exit_code == 0
    assert "version" in result.output.lower()


def test_cli_help() -> None:
    """Test CLI help command."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])

    assert result.exit_code == 0
    assert "compile" in result.output.lower()
    assert "dbt" in result.output.lower()


def test_cli_compile_help() -> None:
    """Test CLI compile subcommand help."""
    runner = CliRunner()
    result = runner.invoke(cli, ["compile", "--help"])

    assert result.exit_code == 0
    assert "--project-dir" in result.output
    assert "--output" in result.output
