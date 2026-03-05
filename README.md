# dbt-skillz

Auto-generate hierarchical Markdown documentation from dbt projects.

**dbt-skillz** parses your dbt project and generates comprehensive, searchable documentation that makes it easy for teams to understand data lineage, model dependencies, and available analytics tables.

## Features

- 📊 **Automatic Documentation** — Parse dbt YAML configs and SQL models in seconds
- 🏗️ **Hierarchical Structure** — Organized by layers (sources → staging → intermediate → marts)
- 🔗 **Lineage Visualization** — Generate Mermaid dependency diagrams
- 📝 **Markdown Output** — Version-control friendly, integrates with docs sites
- 🤖 **AI-Ready** — Output is optimized for use as context in LLM applications
- 🧪 **Well-Tested** — Integration tests with 81%+ code coverage
- 🚀 **Production-Grade** — Type-safe Python, pre-commit hooks, GitHub Actions CI/CD

## Installation

```bash
pip install dbt-skillz
```

## Quick Start

```bash
# Generate documentation for your dbt project
dbt-skillz compile --project-dir ./my_dbt_project --output ./docs/dbt_skills

# Include SQL snippets (useful for understanding transformations)
dbt-skillz compile --project-dir ./my_dbt_project --output ./docs/dbt_skills --include-sql
```

## Output Structure

The generator creates a directory with:

- **`SKILL.md`** — Overview, model inventory, architecture diagram, navigation
- **`ref/sources.md`** — Source system definitions (databases, schemas, tables)
- **`ref/staging.md`** — Staging layer models (data cleaning & typing)
- **`ref/intermediate.md`** — Intermediate models (business logic)
- **`ref/marts.md`** — Mart layer tables (analytics-ready outputs)
- **`ref/macros.md`** — dbt macro reference
- **`ref/lineage.md`** — Dependency graph (Mermaid diagram)

## How It Works

1. **Parse** — Reads `dbt_project.yml`, model YAML configs, SQL files, and macros
2. **Analyze** — Builds an intermediate representation of the project structure
3. **Generate** — Renders Jinja2 templates into hierarchical Markdown

## Example

```bash
$ dbt-skillz compile --project-dir ./analytics --output ./docs

Parsing dbt project at ./analytics ...
  Found 42 models, 5 source tables, 8 macros
    staging: 12 models
    intermediate: 15 models
    marts: 15 models

Generating documentation to ./docs ...
  Generated 7 files:
    SKILL.md (318 lines)
    ref/sources.md (95 lines)
    ref/staging.md (242 lines)
    ref/intermediate.md (156 lines)
    ref/marts.md (487 lines)
    ref/macros.md (84 lines)
    ref/lineage.md (203 lines)

Done.
```

## Use Cases

- **Data Catalog** — Share dbt knowledge with non-technical stakeholders
- **Onboarding** — Help new team members understand data architecture
- **Documentation** — Create version-controlled docs alongside code
- **LLM Context** — Feed to Claude, ChatGPT, etc. for data-aware AI applications

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## License

Apache License 2.0 — See [LICENSE](LICENSE) file for details.
