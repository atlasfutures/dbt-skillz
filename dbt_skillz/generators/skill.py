"""Generator that renders dbt project IR into Markdown documentation files."""

from __future__ import annotations

import re
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape

from ..models import DbtProject, Model

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"

# Default layer descriptions when none can be inferred
LAYER_DESCRIPTIONS: dict[str, str] = {
    "staging": "Clean and type raw source data",
    "intermediate": "Business logic, joins, and enrichment",
    "marts": "Analytics-ready aggregated tables",
    "marts/core": "Dimensional models for joins",
    "marts/analytics": "Report-ready analytical models",
}

# Keyword-to-topic mapping for grouping mart models by business domain.
# Order matters: first match wins. Patterns are checked against model name + description.
# More specific topics come before broader ones to avoid false matches.
TOPIC_KEYWORDS: list[tuple[str, list[str]]] = [
    ("Revenue and Billing", ["revenue", "billing", "payment"]),
    ("Product Usage", ["usage_report", "model_usage", "usage_metric"]),
    ("User Engagement", ["activity", "dau", "wau", "mau", "engagement", "session"]),
    ("Retention and Cohorts", ["cohort", "retention", "churn"]),
    ("Marketing Attribution", ["attribution", "marketing", "campaign", "ad_group", "ad_spend"]),
    ("Acquisition", ["acquisition", "signup"]),
    ("Feature Analysis", ["feature"]),
    ("User Lifecycle", ["journey", "lifecycle"]),
    ("Dimensions", ["dim_"]),
]


def _classify_topic(model: Model) -> str:
    """Classify a model into a topic based on its name and description."""
    text = f"{model.name} {model.description}".lower()
    for topic, keywords in TOPIC_KEYWORDS:
        for kw in keywords:
            if kw in text:
                return topic
    return "Other"


def _build_topic_index(models: list[Model]) -> dict[str, list[Model]]:
    """Group models by business topic."""
    index: dict[str, list[Model]] = {}
    for model in models:
        topic = _classify_topic(model)
        index.setdefault(topic, []).append(model)
    return index


class SkillGenerator:
    """Generates a hierarchical Markdown documentation directory from a DbtProject IR."""

    def __init__(self) -> None:
        self.env = Environment(
            loader=FileSystemLoader(str(TEMPLATES_DIR)),
            autoescape=select_autoescape([]),
            trim_blocks=True,
            lstrip_blocks=True,
            keep_trailing_newline=True,
        )

    def generate(
        self,
        project: DbtProject,
        output_dir: Path,
        *,
        skill_name: str | None = None,
        include_sql: bool = False,
        max_skill_lines: int = 300,
        extras_files: list[Path] | None = None,
    ) -> None:
        """Generate the full skill directory."""
        output_dir = output_dir.resolve()
        ref_dir = output_dir / "ref"
        ref_dir.mkdir(parents=True, exist_ok=True)

        resolved_skill_name = skill_name or f"data-{project.name.replace('_', '-')}"

        # Pre-compute template context helpers
        source_names = ", ".join(s.name for s in project.sources)
        layer_names = ", ".join(project.models.keys())
        layer_materializations = self._resolve_materializations(project)
        layer_descriptions = {layer: LAYER_DESCRIPTIONS.get(layer, "") for layer in project.models}

        # Build topic index for mart models (consumer-facing)
        topic_index = _build_topic_index(project.mart_models)

        # Identify mart vs internal layers
        mart_layers = {k for k in project.models if k.startswith("marts")}
        internal_layers = {k for k in project.models if k not in mart_layers}

        # Render SKILL.md
        self._render_to_file(
            "skill_main.md.j2",
            output_dir / "SKILL.md",
            project=project,
            skill_name=resolved_skill_name,
            source_names=source_names,
            layer_names=layer_names,
            layer_materializations=layer_materializations,
            layer_descriptions=layer_descriptions,
            topic_index=topic_index,
            mart_layers=mart_layers,
            internal_layers=internal_layers,
            include_sql=include_sql,
            extras_files=extras_files or [],
        )

        # Render ref/sources.md
        self._render_to_file(
            "sources.md.j2",
            ref_dir / "sources.md",
            project=project,
        )

        # Render ref/{layer}.md for each layer
        for layer, models in project.models.items():
            layer_file = layer.replace("/", "_")
            mat = layer_materializations.get(layer, "")
            layer_desc = layer_descriptions.get(layer, "")
            is_mart = layer in mart_layers
            self._render_to_file(
                "layer.md.j2",
                ref_dir / f"{layer_file}.md",
                layer=layer,
                models=models,
                materialization=mat,
                layer_description=layer_desc,
                is_mart=is_mart,
                include_sql=include_sql,
            )

        # Render ref/macros.md
        self._render_to_file(
            "macros.md.j2",
            ref_dir / "macros.md",
            project=project,
            include_sql=include_sql,
        )

        # Render ref/lineage.md
        self._render_to_file(
            "lineage.md.j2",
            ref_dir / "lineage.md",
            project=project,
        )

        # Post-process: enforce line budget on SKILL.md
        self._enforce_line_budget(output_dir / "SKILL.md", max_skill_lines)

    def _render_to_file(self, template_name: str, output_path: Path, **context: object) -> None:
        """Render a Jinja2 template to a file."""
        template = self.env.get_template(template_name)
        content = template.render(**context)
        # Clean up excessive blank lines (more than 2 consecutive)
        content = re.sub(r"\n{4,}", "\n\n\n", content)
        output_path.write_text(content)

    def _resolve_materializations(self, project: DbtProject) -> dict[str, str]:
        """Resolve materialization for each layer from project config or model defaults."""
        result: dict[str, str] = {}
        for layer, models in project.models.items():
            # Check if any model in the layer has an explicit materialization
            mats = [m.materialized for m in models if m.materialized]
            if mats:
                result[layer] = mats[0]
            else:
                # Derive from project config layer structure
                result[layer] = self._materialization_from_config(layer, project.model_configs)
        return result

    def _materialization_from_config(self, layer: str, model_configs: dict[str, object]) -> str:
        """Walk project model configs to find materialization for a layer path."""
        parts = layer.split("/")
        config = model_configs
        for part in parts:
            if not isinstance(config, dict):
                return ""
            config = config.get(part, {})  # type: ignore[assignment]
        if isinstance(config, dict):
            return str(config.get("+materialized", ""))
        return ""

    def _enforce_line_budget(self, path: Path, max_lines: int) -> None:
        """If SKILL.md exceeds max_lines, truncate the Available Data section."""
        content = path.read_text()
        lines = content.split("\n")
        if len(lines) <= max_lines:
            return

        # Find the "## Available Data" section and truncate it
        truncation_start = None
        truncation_end = None
        for i, line in enumerate(lines):
            if line.strip() == "## Available Data":
                truncation_start = i
            elif (
                truncation_start is not None and line.startswith("## ") and i > truncation_start + 1
            ):
                truncation_end = i
                break

        if truncation_start is not None:
            end = truncation_end or len(lines)
            replacement = [
                "## Available Data",
                "",
                "See the quick reference table below and mart reference files for full details.",
                "",
            ]
            lines = lines[:truncation_start] + replacement + lines[end:]
            path.write_text("\n".join(lines))
