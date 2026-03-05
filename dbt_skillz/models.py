"""Intermediate representation for parsed data projects."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class Column:
    """A column in a source table or model."""

    name: str
    description: str = ""
    data_type: str = ""
    tests: list[str] = field(default_factory=list)


@dataclass
class SourceTable:
    """A table within a source system."""

    name: str
    description: str = ""
    columns: list[Column] = field(default_factory=list)


@dataclass
class Source:
    """A source system (database/schema) containing raw tables."""

    name: str
    database: str = ""
    schema: str = ""
    description: str = ""
    tables: list[SourceTable] = field(default_factory=list)


@dataclass
class ModelTest:
    """A test defined on a model or column."""

    name: str
    column: str = ""
    config: dict[str, Any] = field(default_factory=dict)


@dataclass
class Model:
    """A dbt model (SQL transformation)."""

    name: str
    description: str = ""
    sql_path: str = ""
    materialized: str = ""
    schema: str = ""
    grain: str = ""
    tags: list[str] = field(default_factory=list)
    columns: list[Column] = field(default_factory=list)
    tests: list[ModelTest] = field(default_factory=list)
    refs: list[str] = field(default_factory=list)
    sources: list[tuple[str, str]] = field(default_factory=list)
    sql_content: str = ""
    config: dict[str, Any] = field(default_factory=dict)
    enabled: bool = True

    @property
    def queryable_name(self) -> str:
        """The queryable table/view name: schema.model_name."""
        if self.schema:
            return f"{self.schema}.{self.name}"
        return self.name


@dataclass
class Macro:
    """A dbt macro."""

    name: str
    arguments: list[str] = field(default_factory=list)
    description: str = ""
    sql_path: str = ""
    sql_content: str = ""


@dataclass
class DbtProject:
    """Complete parsed representation of a dbt project."""

    name: str
    version: str = ""
    profile: str = ""
    sources: list[Source] = field(default_factory=list)
    models: dict[str, list[Model]] = field(default_factory=dict)
    macros: list[Macro] = field(default_factory=list)
    variables: dict[str, Any] = field(default_factory=dict)
    model_configs: dict[str, Any] = field(default_factory=dict)
    project_dir: str = ""

    @property
    def all_models(self) -> list[Model]:
        """Flat list of all models across layers."""
        return [m for models in self.models.values() for m in models]

    @property
    def lineage(self) -> dict[str, list[str]]:
        """Build dependency graph: model_name -> list of upstream model/source names."""
        graph: dict[str, list[str]] = {}
        for model in self.all_models:
            deps: list[str] = []
            deps.extend(model.refs)
            deps.extend(f"{src}.{tbl}" for src, tbl in model.sources)
            graph[model.name] = deps
        return graph

    @property
    def total_model_count(self) -> int:
        return len(self.all_models)

    @property
    def total_source_table_count(self) -> int:
        return sum(len(s.tables) for s in self.sources)

    @property
    def mart_models(self) -> list[Model]:
        """All models in mart layers (consumer-facing tables)."""
        return [
            m for layer, models in self.models.items() if layer.startswith("marts") for m in models
        ]
