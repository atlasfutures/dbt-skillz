"""Tests for the dbt parser."""

from __future__ import annotations

from pathlib import Path

from dbt_skillz.parsers.dbt import DbtParser


def test_parse_basic_project(fixture_project_dir: Path) -> None:
    """Test parsing a basic dbt project."""
    parser = DbtParser()
    project = parser.parse(fixture_project_dir)

    # Check project metadata
    assert project.name == "test_project"
    assert project.version == "1.0.0"

    # Check models grouped by layer
    assert "staging" in project.models
    assert "intermediate" in project.models
    assert "marts" in project.models

    # Check staging models
    staging_models = project.models["staging"]
    assert len(staging_models) == 2
    staging_names = {m.name for m in staging_models}
    assert "stg_firestore__users" in staging_names
    assert "stg_analytics__events" in staging_names

    # Check intermediate models
    intermediate_models = project.models["intermediate"]
    assert len(intermediate_models) == 1
    assert intermediate_models[0].name == "int_user_events"

    # Check mart models
    mart_models = project.models["marts"]
    assert len(mart_models) == 1
    assert mart_models[0].name == "user_activity_report"

    # Check total counts
    assert project.total_model_count == 4
    assert project.total_source_table_count == 2  # 1 from firestore, 1 from analytics


def test_parse_sources(fixture_project_dir: Path) -> None:
    """Test source parsing."""
    parser = DbtParser()
    project = parser.parse(fixture_project_dir)

    assert len(project.sources) == 2

    # Find firestore source
    firestore_source = next((s for s in project.sources if s.name == "firestore"), None)
    assert firestore_source is not None
    assert firestore_source.database == "test_project"
    assert firestore_source.schema == "raw_firestore"
    assert len(firestore_source.tables) == 1
    assert firestore_source.tables[0].name == "users"

    # Find analytics source
    analytics_source = next((s for s in project.sources if s.name == "analytics"), None)
    assert analytics_source is not None
    assert analytics_source.schema == "raw_analytics"
    assert len(analytics_source.tables) == 1
    assert analytics_source.tables[0].name == "events"


def test_parse_model_columns(fixture_project_dir: Path) -> None:
    """Test that model columns are parsed from YAML."""
    parser = DbtParser()
    project = parser.parse(fixture_project_dir)

    # Get the user_activity_report model
    mart_models = project.models["marts"]
    user_activity = next((m for m in mart_models if m.name == "user_activity_report"), None)
    assert user_activity is not None

    # Check columns
    assert len(user_activity.columns) == 4
    column_names = {c.name for c in user_activity.columns}
    assert "user_id" in column_names
    assert "email" in column_names
    assert "total_events" in column_names

    # Check column descriptions
    user_id_col = next((c for c in user_activity.columns if c.name == "user_id"), None)
    assert user_id_col is not None
    assert "Primary key" in user_id_col.description


def test_parse_model_refs_and_sources(fixture_project_dir: Path) -> None:
    """Test that model dependencies (refs and sources) are extracted."""
    parser = DbtParser()
    project = parser.parse(fixture_project_dir)

    # Get the stg_firestore__users model
    staging_models = project.models["staging"]
    stg_users = next((m for m in staging_models if m.name == "stg_firestore__users"), None)
    assert stg_users is not None

    # Check that it references the firestore.users source
    assert len(stg_users.sources) == 1
    assert stg_users.sources[0] == ("firestore", "users")

    # Get the int_user_events model
    intermediate_models = project.models["intermediate"]
    int_events = next((m for m in intermediate_models if m.name == "int_user_events"), None)
    assert int_events is not None

    # Check refs to staging models
    assert len(int_events.refs) == 2
    assert "stg_analytics__events" in int_events.refs
    assert "stg_firestore__users" in int_events.refs


def test_parse_macros(fixture_project_dir: Path) -> None:
    """Test macro parsing."""
    parser = DbtParser()
    project = parser.parse(fixture_project_dir)

    # We should have parsed at least one macro
    assert len(project.macros) >= 1

    # Check for the generate_alias_name macro
    alias_macro = next((m for m in project.macros if m.name == "generate_alias_name"), None)
    assert alias_macro is not None
    assert alias_macro.name == "generate_alias_name"

    # Check for the cents_to_dollars macro
    cents_macro = next((m for m in project.macros if m.name == "cents_to_dollars"), None)
    assert cents_macro is not None
    assert "column_name" in cents_macro.arguments


def test_parse_variables(fixture_project_dir: Path) -> None:
    """Test that variables are extracted."""
    parser = DbtParser()
    project = parser.parse(fixture_project_dir)

    assert len(project.variables) == 2
    assert project.variables.get("key_1") == "value_1"
    assert project.variables.get("key_2") == "value_2"


def test_lineage_graph(fixture_project_dir: Path) -> None:
    """Test the lineage dependency graph."""
    parser = DbtParser()
    project = parser.parse(fixture_project_dir)

    lineage = project.lineage
    assert lineage is not None

    # Check that int_user_events depends on staging models
    assert "int_user_events" in lineage
    int_deps = lineage["int_user_events"]
    assert "stg_analytics__events" in int_deps
    assert "stg_firestore__users" in int_deps

    # Check that staging models depend on sources
    assert "stg_firestore__users" in lineage
    stg_deps = lineage["stg_firestore__users"]
    assert "firestore.users" in stg_deps
