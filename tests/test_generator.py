"""Tests for the skill generator."""

from __future__ import annotations

import tempfile
from pathlib import Path

from dbt_skillz.compiler import compile_dbt_project
from dbt_skillz.generators.skill import SkillGenerator
from dbt_skillz.parsers.dbt import DbtParser


def test_generate_outputs_directory_structure(fixture_project_dir: Path) -> None:
    """Test that the generator creates the expected directory structure."""
    parser = DbtParser()
    project = parser.parse(fixture_project_dir)

    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir) / "output"
        generator = SkillGenerator()
        generator.generate(project, output_dir)

        # Check that the output directory was created
        assert output_dir.exists()

        # Check for main SKILL.md file
        skill_file = output_dir / "SKILL.md"
        assert skill_file.exists()

        # Check for reference directory
        ref_dir = output_dir / "ref"
        assert ref_dir.exists()

        # Check for individual reference files
        expected_files = [
            "sources.md",
            "staging.md",
            "intermediate.md",
            "marts.md",
            "macros.md",
            "lineage.md",
        ]
        for filename in expected_files:
            ref_file = ref_dir / filename
            assert ref_file.exists(), f"Missing {filename}"


def test_skill_md_content(fixture_project_dir: Path) -> None:
    """Test that SKILL.md contains expected content."""
    parser = DbtParser()
    project = parser.parse(fixture_project_dir)

    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir) / "output"
        generator = SkillGenerator()
        generator.generate(project, output_dir)

        skill_file = output_dir / "SKILL.md"
        content = skill_file.read_text()

        # Check for expected sections
        assert "test_project" in content
        assert "Overview" in content
        assert "Quick Reference" in content
        assert "Architecture" in content
        assert "Navigation" in content

        # Check for model references
        assert "user_activity_report" in content


def test_sources_md_content(fixture_project_dir: Path) -> None:
    """Test that sources.md contains expected content."""
    parser = DbtParser()
    project = parser.parse(fixture_project_dir)

    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir) / "output"
        generator = SkillGenerator()
        generator.generate(project, output_dir)

        sources_file = output_dir / "ref" / "sources.md"
        content = sources_file.read_text()

        # Check for source names
        assert "firestore" in content
        assert "analytics" in content

        # Check for schema and database info
        assert "raw_firestore" in content
        assert "raw_analytics" in content

        # Check for table names
        assert "users" in content
        assert "events" in content


def test_mart_layer_md_content(fixture_project_dir: Path) -> None:
    """Test that marts layer reference file contains expected content."""
    parser = DbtParser()
    project = parser.parse(fixture_project_dir)

    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir) / "output"
        generator = SkillGenerator()
        generator.generate(project, output_dir)

        marts_file = output_dir / "ref" / "marts.md"
        content = marts_file.read_text()

        # Check for mart model name
        assert "user_activity_report" in content

        # Check for column information
        assert "user_id" in content
        assert "email" in content
        assert "total_events" in content

        # Check for description
        assert "Analytical report" in content or "activity" in content.lower()


def test_lineage_md_content(fixture_project_dir: Path) -> None:
    """Test that lineage.md contains mermaid diagram."""
    parser = DbtParser()
    project = parser.parse(fixture_project_dir)

    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir) / "output"
        generator = SkillGenerator()
        generator.generate(project, output_dir)

        lineage_file = output_dir / "ref" / "lineage.md"
        content = lineage_file.read_text()

        # Check for mermaid diagram
        assert "mermaid" in content.lower() or "graph" in content

        # Check for model names in the diagram
        assert "int_user_events" in content or "stg_" in content


def test_macros_md_content(fixture_project_dir: Path) -> None:
    """Test that macros.md contains macro definitions."""
    parser = DbtParser()
    project = parser.parse(fixture_project_dir)

    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir) / "output"
        generator = SkillGenerator()
        generator.generate(project, output_dir)

        macros_file = output_dir / "ref" / "macros.md"
        content = macros_file.read_text()

        # Check for macro names
        assert "generate_alias_name" in content
        assert "cents_to_dollars" in content


def test_compile_dbt_project_full_pipeline(fixture_project_dir: Path) -> None:
    """Integration test: full compile_dbt_project pipeline."""
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir) / "output"
        compile_dbt_project(
            project_dir=fixture_project_dir,
            output_dir=output_dir,
        )

        # Check that all expected files exist
        assert (output_dir / "SKILL.md").exists()
        assert (output_dir / "ref" / "sources.md").exists()
        assert (output_dir / "ref" / "staging.md").exists()
        assert (output_dir / "ref" / "marts.md").exists()

        # Check file content is non-empty
        skill_content = (output_dir / "SKILL.md").read_text()
        assert len(skill_content) > 100
