"""Parser for dbt projects -- reads YAML configs, SQL models, and macros."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import yaml

from ..models import (
    Column,
    DbtProject,
    Macro,
    Model,
    ModelTest,
    Source,
    SourceTable,
)

# Regex patterns for extracting dbt dependencies from SQL
REF_PATTERN = re.compile(r"\{\{\s*ref\(\s*['\"](\w+)['\"]\s*\)\s*\}\}")
SOURCE_PATTERN = re.compile(r"\{\{\s*source\(\s*['\"](\w+)['\"],\s*['\"](\w+)['\"]\s*\)\s*\}\}")
# Regex for dbt config blocks: {{ config(...) }}
CONFIG_PATTERN = re.compile(r"\{\{\s*config\s*\(([^)]*)\)\s*\}\}", re.DOTALL)
# Regex for macro definitions: {% macro name(args) %}
MACRO_PATTERN = re.compile(r"\{%[-\s]*macro\s+(\w+)\s*\(([^)]*)\)\s*[-]?%\}")
# Regex for Jinja doc comments: {# ... #}
DOC_COMMENT_PATTERN = re.compile(r"\{#(.*?)#\}", re.DOTALL)
# Regex for SQL block comments: /* ... */
SQL_COMMENT_PATTERN = re.compile(r"/\*(.*?)\*/", re.DOTALL)
# Regex for dbt config enabled=false
ENABLED_FALSE_PATTERN = re.compile(r"""config\s*\([^)]*enabled\s*=\s*(?:false|False)""", re.DOTALL)


class DbtParser:
    """Parses a dbt project directory into the IR."""

    def parse(self, project_dir: Path) -> DbtProject:
        """Parse the dbt project at project_dir and return a DbtProject IR."""
        project_dir = project_dir.resolve()

        # Parse dbt_project.yml
        project_config = self._parse_project_yml(project_dir / "dbt_project.yml")

        # Determine paths from config
        model_paths = project_config.get("model-paths", ["models"])
        macro_paths = project_config.get("macro-paths", ["macros"])

        # Parse sources
        sources = self._parse_sources(project_dir, model_paths)

        # Parse model schemas (_*__models.yml files)
        schema_map = self._parse_model_schemas(project_dir, model_paths)

        # Parse SQL model files and build layer map
        models = self._parse_sql_models(project_dir, model_paths, schema_map, project_config)

        # Parse macros
        macros = self._parse_macros(project_dir, macro_paths)

        # Extract variables
        variables = project_config.get("vars", {})

        # Extract model configs from dbt_project.yml
        project_name = project_config.get("name", "")
        model_configs = project_config.get("models", {}).get(project_name, {})

        return DbtProject(
            name=project_name,
            version=project_config.get("version", ""),
            profile=project_config.get("profile", ""),
            sources=sources,
            models=models,
            macros=macros,
            variables=variables,
            model_configs=model_configs,
            project_dir=str(project_dir),
        )

    def _parse_project_yml(self, path: Path) -> dict[str, Any]:
        """Parse dbt_project.yml."""
        if not path.exists():
            raise FileNotFoundError(f"dbt_project.yml not found at {path}")
        with open(path) as f:
            return yaml.safe_load(f) or {}

    def _parse_sources(self, project_dir: Path, model_paths: list[str]) -> list[Source]:
        """Find and parse all sources.yml files."""
        sources: list[Source] = []
        for mp in model_paths:
            models_dir = project_dir / mp
            if not models_dir.exists():
                continue
            for yml_path in models_dir.rglob("sources.yml"):
                sources.extend(self._parse_source_file(yml_path))
        return sources

    def _parse_source_file(self, path: Path) -> list[Source]:
        """Parse a single sources.yml file."""
        with open(path) as f:
            data = yaml.safe_load(f) or {}

        sources: list[Source] = []
        for src in data.get("sources", []):
            tables: list[SourceTable] = []
            for tbl in src.get("tables", []):
                columns = [
                    Column(
                        name=col.get("name", ""),
                        description=col.get("description", ""),
                    )
                    for col in tbl.get("columns", [])
                ]
                tables.append(
                    SourceTable(
                        name=tbl.get("name", ""),
                        description=tbl.get("description", ""),
                        columns=columns,
                    )
                )
            sources.append(
                Source(
                    name=src.get("name", ""),
                    database=src.get("database", ""),
                    schema=src.get("schema", ""),
                    description=src.get("description", ""),
                    tables=tables,
                )
            )
        return sources

    def _parse_model_schemas(
        self, project_dir: Path, model_paths: list[str]
    ) -> dict[str, dict[str, Any]]:
        """Parse all _*__models.yml schema files into a map of model_name -> schema dict."""
        schema_map: dict[str, dict[str, Any]] = {}
        for mp in model_paths:
            models_dir = project_dir / mp
            if not models_dir.exists():
                continue
            for yml_path in models_dir.rglob("*.yml"):
                # Skip sources.yml, match schema files like _firestore__models.yml
                if yml_path.name == "sources.yml":
                    continue
                with open(yml_path) as f:
                    data = yaml.safe_load(f) or {}
                for model_def in data.get("models", []):
                    name = model_def.get("name", "")
                    if name:
                        schema_map[name] = model_def
        return schema_map

    def _parse_sql_models(
        self,
        project_dir: Path,
        model_paths: list[str],
        schema_map: dict[str, dict[str, Any]],
        project_config: dict[str, Any],
    ) -> dict[str, list[Model]]:
        """Parse all SQL model files and organize by layer."""
        project_name = project_config.get("name", "")
        model_configs = project_config.get("models", {}).get(project_name, {})
        models: dict[str, list[Model]] = {}

        for mp in model_paths:
            models_dir = project_dir / mp
            if not models_dir.exists():
                continue
            for sql_path in models_dir.rglob("*.sql"):
                layer = self._determine_layer(sql_path, models_dir)
                model = self._parse_sql_model(sql_path, models_dir, schema_map, project_config)
                if model is None:
                    continue
                # Resolve schema from project config (+schema)
                model.schema = self._resolve_schema_for_layer(layer, model_configs)
                # Detect grain from columns with unique+not_null tests
                model.grain = self._detect_grain(model)
                models.setdefault(layer, []).append(model)

        # Sort models within each layer by name
        for layer in models:
            models[layer].sort(key=lambda m: m.name)

        # Sort layers by name for deterministic output across filesystems
        return dict(sorted(models.items()))

    def _parse_sql_model(
        self,
        sql_path: Path,
        models_dir: Path,
        schema_map: dict[str, dict[str, Any]],
        project_config: dict[str, Any],
    ) -> Model | None:
        """Parse a single SQL model file."""
        model_name = sql_path.stem
        sql_content = sql_path.read_text()

        # Check if model is disabled in SQL config block
        if ENABLED_FALSE_PATTERN.search(sql_content):
            return None

        # Check if disabled in schema
        schema = schema_map.get(model_name, {})
        if schema.get("config", {}).get("enabled") is False:
            return None

        # Extract refs and sources from SQL
        refs = REF_PATTERN.findall(sql_content)
        source_deps = SOURCE_PATTERN.findall(sql_content)

        # Extract config block from SQL
        config = self._extract_sql_config(sql_content)

        # Build columns from schema
        columns = self._build_columns(schema)

        # Build tests from schema
        tests = self._build_tests(schema)

        # Determine materialization from config or project defaults
        materialized = config.get("materialized", "")

        # Get relative path from models dir
        rel_path = str(sql_path.relative_to(models_dir))

        return Model(
            name=model_name,
            description=schema.get("description", config.get("description", "")),
            sql_path=rel_path,
            materialized=materialized,
            columns=columns,
            tests=tests,
            refs=sorted(set(refs)),
            sources=sorted(set(source_deps)),
            sql_content=sql_content,
            config=config,
            enabled=True,
        )

    def _extract_sql_config(self, sql_content: str) -> dict[str, Any]:
        """Extract config values from {{ config(...) }} block in SQL."""
        match = CONFIG_PATTERN.search(sql_content)
        if not match:
            return {}

        config_str = match.group(1).strip()
        # Simple key-value extraction for common config keys
        config: dict[str, Any] = {}
        # Match key='value' or key="value" patterns
        for kv_match in re.finditer(r"(\w+)\s*=\s*(?:'([^']*)'|\"([^\"]*)\"|(\w+))", config_str):
            key = kv_match.group(1)
            value = kv_match.group(2) or kv_match.group(3) or kv_match.group(4)
            if value in ("true", "True"):
                config[key] = True
            elif value in ("false", "False"):
                config[key] = False
            else:
                config[key] = value
        return config

    def _build_columns(self, schema: dict[str, Any]) -> list[Column]:
        """Build Column objects from schema definition."""
        columns: list[Column] = []
        for col_def in schema.get("columns", []):
            test_names: list[str] = []
            for test in col_def.get("tests", []):
                if isinstance(test, str):
                    test_names.append(test)
                elif isinstance(test, dict):
                    test_names.extend(test.keys())
            columns.append(
                Column(
                    name=col_def.get("name", ""),
                    description=col_def.get("description", ""),
                    data_type=col_def.get("data_type", ""),
                    tests=test_names,
                )
            )
        return columns

    def _build_tests(self, schema: dict[str, Any]) -> list[ModelTest]:
        """Build ModelTest objects from schema definition (model-level tests)."""
        tests: list[ModelTest] = []
        for col_def in schema.get("columns", []):
            col_name = col_def.get("name", "")
            for test in col_def.get("tests", []):
                if isinstance(test, str):
                    tests.append(ModelTest(name=test, column=col_name))
                elif isinstance(test, dict):
                    for test_name, test_config in test.items():
                        tests.append(
                            ModelTest(
                                name=test_name,
                                column=col_name,
                                config=test_config if isinstance(test_config, dict) else {},
                            )
                        )
        return tests

    def _determine_layer(self, sql_path: Path, models_dir: Path) -> str:
        """Determine the dbt layer (staging, intermediate, marts, etc.) from file path."""
        rel_parts = sql_path.relative_to(models_dir).parts
        if len(rel_parts) >= 2:
            # First directory under models/ is the layer
            layer = rel_parts[0]
            # For marts, include the sub-layer (e.g., "marts/core", "marts/analytics")
            if layer == "marts" and len(rel_parts) >= 3:
                return f"{layer}/{rel_parts[1]}"
            return layer
        return "other"

    def _resolve_schema_for_layer(self, layer: str, model_configs: dict[str, Any]) -> str:
        """Walk project model configs to find +schema for a layer path.

        For "marts/analytics", walks: model_configs["marts"] first (which has +schema),
        then optionally into ["analytics"]. The +schema from the nearest ancestor applies.
        """
        parts = layer.split("/")
        config = model_configs
        schema = ""
        for part in parts:
            if not isinstance(config, dict):
                break
            config = config.get(part, {})
            if isinstance(config, dict) and "+schema" in config:
                schema = str(config["+schema"])
        return schema

    def _detect_grain(self, model: Model) -> str:
        """Detect the grain of a model from columns that have both unique and not_null tests.

        Columns with unique+not_null constraints define the model's primary key / grain.
        """
        grain_columns: list[str] = []
        for col in model.columns:
            has_unique = "unique" in col.tests
            has_not_null = "not_null" in col.tests
            if has_unique and has_not_null:
                grain_columns.append(col.name)

        if not grain_columns:
            return ""

        # Map common column names to human-readable grain descriptions
        grain_labels: dict[str, str] = {
            "date": "daily",
            "date_key": "daily",
            "cohort_month": "monthly cohort",
        }
        if len(grain_columns) == 1:
            col = grain_columns[0]
            return grain_labels.get(col, f"one row per {col}")

        # Multiple grain columns: composite key -- deduplicate labels
        labels: list[str] = []
        seen: set[str] = set()
        for c in grain_columns:
            label = grain_labels.get(c, c)
            if label not in seen:
                labels.append(label)
                seen.add(label)

        if len(labels) == 1:
            return labels[0]
        return "one row per " + " + ".join(labels)

    def _parse_macros(self, project_dir: Path, macro_paths: list[str]) -> list[Macro]:
        """Parse all macro SQL files."""
        macros: list[Macro] = []
        for mp in macro_paths:
            macros_dir = project_dir / mp
            if not macros_dir.exists():
                continue
            for sql_path in macros_dir.rglob("*.sql"):
                macros.extend(self._parse_macro_file(sql_path, macros_dir))
        macros.sort(key=lambda m: m.name)
        return macros

    def _parse_macro_file(self, path: Path, macros_dir: Path) -> list[Macro]:
        """Parse macros from a single SQL file."""
        content = path.read_text()
        rel_path = str(path.relative_to(macros_dir))

        # Find all doc comments (for description mapping)
        doc_comments = DOC_COMMENT_PATTERN.findall(content)

        # Find all macro definitions
        results: list[Macro] = []
        for i, match in enumerate(MACRO_PATTERN.finditer(content)):
            macro_name = match.group(1)
            args_str = match.group(2).strip()
            arguments = [a.strip() for a in args_str.split(",") if a.strip()] if args_str else []

            # Try to associate the most recent doc comment before this macro
            description = ""
            if i < len(doc_comments):
                desc_text = doc_comments[i].strip()
                # Extract the first "Macro: ..." line and the description
                lines = desc_text.split("\n")
                desc_parts: list[str] = []
                for line in lines:
                    stripped = line.strip()
                    if stripped.startswith("Macro:"):
                        continue
                    if (
                        stripped.startswith("Usage")
                        or stripped.startswith("Arguments:")
                        or stripped.startswith("Returns:")
                    ):
                        break
                    if stripped:
                        desc_parts.append(stripped)
                description = " ".join(desc_parts)

            results.append(
                Macro(
                    name=macro_name,
                    arguments=arguments,
                    description=description,
                    sql_path=rel_path,
                    sql_content=content,
                )
            )
        return results
