# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-03-05

### Changed

- **README rewrite** — New value-first positioning: "Make your dbt project AI-readable"
- Updated package metadata:
  - Author: Workshop AI <hello@workshop.ai>
  - Keywords: dbt, documentation, llm, ai, data-engineering, markdown, context
  - Status: Beta (was Alpha)
- Improved PyPI-friendly README with badges and clear structure

### Fixed

- Jinja2 templates now included in wheel package (setuptools package-data)

## [0.1.1] - 2024-03-04

### Fixed

- Jinja2 templates now included in wheel package (setuptools package-data)

## [0.1.0] - 2024-03-04

### Added

- Initial release: Auto-generate Markdown documentation from dbt projects
- Parse dbt project structure (models, sources, macros)
- Generate hierarchical documentation with:
  - Overview and model inventory
  - Per-layer reference documents (sources, staging, intermediate, marts)
  - Macro definitions
  - Dependency lineage (Mermaid diagrams)
- CLI command: `dbt-skillz compile`
- Options:
  - `--project-dir` — Path to dbt project
  - `--output` — Output directory for documentation
  - `--skill-name` — Override auto-detected project name
  - `--include-sql` — Include SQL snippets in reference docs
  - `--max-skill-lines` — Limit main SKILL.md size
  - `--extras-dir` — Static markdown files to copy alongside output
- Integration test suite (20+ tests, 81% code coverage)
- GitHub Actions CI/CD:
  - Test matrix: Python 3.10, 3.11, 3.12, 3.13 on Linux
  - Linting (ruff) and type checking (basedpyright)
  - Auto-publish to PyPI on git tags
- Documentation:
  - README with quick-start guide
  - CONTRIBUTING guide for development
  - CHANGELOG (this file)

### Changed

- Renamed `data-skillz` → `dbt-skillz` for clarity
- Renamed `ClaudeSkillGenerator` → `SkillGenerator` (decoupled from Claude branding)
- Updated help text and docstrings to be domain-neutral
- Changed default output path from `.claude/skills/` → `.dbt_skills/`

### Removed

- Claude-specific branding and references
- Hardcoded paths and internal configurations

## Unreleased

### Planned

- Support for dbt artifacts (manifest.json, run_results.json)
- JSON output format for programmatic access
- Configuration file support (dbt-skillz.yml)
- Custom Jinja2 template support
- HTML output format
- Integration with dbt documentation site
