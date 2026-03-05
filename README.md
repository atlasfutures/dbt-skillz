# dbt-skillz

<p align="center">
  <strong>Turn your dbt project into an AI agent skill</strong>
</p>

<p align="center">
  <em>Compatible with Claude Code, <a href="https://workshop.ai?utm_source=dbt-skillz-github&utm_medium=readme&utm_campaign=agent-partnerships&utm_content=link">Workshop</a>, Cursor, and any agent that reads Markdown</em>
</p>

<p align="center">
  <a href="https://pypi.org/project/dbt-skillz/">
    <img src="https://img.shields.io/pypi/v/dbt-skillz.svg?color=4B78E6&label=PyPI" alt="PyPI version" />
  </a>
  <a href="https://github.com/atlasfutures/dbt-skillz/actions/workflows/ci.yml">
    <img src="https://github.com/atlasfutures/dbt-skillz/actions/workflows/ci.yml/badge.svg" alt="CI" />
  </a>
  <a href="https://pypi.org/project/dbt-skillz/">
    <img src="https://img.shields.io/pypi/pyversions/dbt-skillz.svg?color=73DC8C" alt="Python versions" />
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/License-Apache%202.0-FA9BFA.svg" alt="License" />
  </a>
</p>

---

Your dbt project contains everything an AI needs to work with your data — table structures, column types, transformations, lineage. But that knowledge is scattered across YAML files and SQL that agents can't efficiently parse.

**dbt-skillz compiles your dbt project into an agent skill** — structured Markdown that AI agents can ingest as context. Now when you ask Claude to write a query or Cursor to debug a transformation, it actually understands your data architecture.

Works with:
- **Claude Code** — Drop the skill in `.claude/` or attach to conversations
- **[Workshop](https://workshop.ai?utm_source=dbt-skillz-github&utm_medium=readme&utm_campaign=agent-partnerships&utm_content=link)** — Add as a project skill for data-aware AI assistance
- **Cursor** — Include in your codebase context
- **Any Markdown-aware agent** — Universal compatibility

## Quick Start

```bash
pip install dbt-skillz

dbt-skillz compile --project-dir ./analytics --output ./docs
```

Point your agent at the generated `SKILL.md` and it now understands your entire dbt project.

## What You Get

```
docs/
├── SKILL.md              # Agent-ready overview (the main skill file)
└── ref/
    ├── sources.md        # Source tables (databases, schemas, tables)
    ├── staging.md        # Staging models (cleaned & typed)
    ├── intermediate.md   # Intermediate models (business logic)
    ├── marts.md          # Mart tables (analytics-ready)
    ├── macros.md         # dbt macro reference
    └── lineage.md        # Mermaid dependency graph
```

The `SKILL.md` file is the entry point your agent reads. It contains:
- Project architecture overview
- Model inventory by layer
- Navigation links to detailed references
- Mermaid lineage diagram

## Why Agent Skills Matter

When you give an AI context about your data, it stops guessing and starts knowing:

| Without dbt-skillz | With dbt-skillz |
|-------------------|-----------------|
| "Write a query for user revenue" | "Write a query using `revenue_report` mart table, joining on `user_id`" |
| "Debug this failing model" | "The error is in `int_daily_usage` which depends on `stg_firestore__daily_usage`" |
| "What tables are available?" | "Your marts include `revenue_report`, `usage_report`, `cohort_retention`..." |

## Use Cases

### Claude Code / Cursor Integration

```bash
# Generate skill into your project
dbt-skillz compile --project-dir ./analytics --output ./.claude/skills/data-analytics

# Or attach SKILL.md directly in conversations
```

Claude now knows your table names, column types, and transformation logic before writing a single line of code.

### Workshop Integration

Add the generated skill to your [Workshop](https://workshop.ai?utm_source=dbt-skillz-github&utm_medium=readme&utm_campaign=agent-partnerships&utm_content=link) project. When you ask "build a dashboard for monthly revenue", Workshop references your actual `revenue_report` table with correct column names.

### Team Onboarding

New data engineer joining? Point them to `SKILL.md` for architecture overview and `ref/lineage.md` to understand dependencies. Same files the AI uses — humans can read them too.

## Installation

```bash
# pip
pip install dbt-skillz

# uv
uv tool install dbt-skillz

# pipx
pipx install dbt-skillz
```

## CLI Reference

```bash
dbt-skillz compile [OPTIONS]

Options:
  --project-dir PATH    Path to dbt project root [default: current directory]
  --output PATH         Output directory for generated skill [required]
  --extras-dir PATH     Additional markdown to include (e.g., workflow docs)
  --include-sql         Include SQL snippets in model documentation
  --skill-name TEXT     Override auto-detected project name
  --max-skill-lines N   Limit SKILL.md size (default: 800)
  --help                Show this message and exit
```

### Examples

```bash
# Basic usage
dbt-skillz compile --project-dir ./analytics --output ./docs

# Generate for Claude Code
dbt-skillz compile --project-dir ./analytics --output ./.claude/skills/analytics

# Include SQL transformations
dbt-skillz compile --project-dir ./analytics --output ./docs --include-sql

# Add custom documentation (workflow guides, conventions, etc.)
dbt-skillz compile --project-dir ./analytics --extras-dir ./skill_extras --output ./docs
```

## Example Output

```bash
$ dbt-skillz compile --project-dir ./analytics --output ./docs

Parsing dbt project at ./analytics ...
  Found 42 models, 5 sources, 8 macros
    staging: 12 models
    intermediate: 15 models
    marts: 15 models

Generating agent skill to ./docs ...
  SKILL.md (318 lines)
  ref/sources.md (95 lines)
  ref/staging.md (242 lines)
  ref/intermediate.md (156 lines)
  ref/marts.md (487 lines)
  ref/macros.md (84 lines)
  ref/lineage.md (203 lines)

Done. Point your agent at SKILL.md to get started.
```

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## License

Apache License 2.0 — See [LICENSE](LICENSE) for details.
