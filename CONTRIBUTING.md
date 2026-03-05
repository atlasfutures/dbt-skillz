# Contributing to dbt-skillz

Thank you for your interest in contributing! This document provides guidelines and instructions for development.

## Development Setup

### Prerequisites

- Python 3.10+
- [uv](https://docs.astral.sh/uv/) (fast Python package manager)

### Local Setup

```bash
# Clone the repository
git clone https://github.com/atlasfutures/dbt-skillz.git
cd dbt-skillz

# Install development dependencies
uv sync --extra dev

# Activate the virtual environment
source .venv/bin/activate
```

## Testing

### Run Tests

```bash
# Run all tests with coverage
pytest tests/ -v --cov=dbt_skillz

# Run specific test file
pytest tests/test_parser.py -v

# Run specific test function
pytest tests/test_parser.py::test_parse_basic_project -v
```

### Code Quality

```bash
# Lint with ruff
ruff check dbt_skillz tests --fix

# Format code
ruff format dbt_skillz tests

# Type check with basedpyright
basedpyright dbt_skillz
```

Run all checks locally before pushing:

```bash
# Run all CI checks locally (linting, type checking, tests)
ruff check dbt_skillz tests
ruff format --check dbt_skillz tests
basedpyright dbt_skillz
pytest tests/ -v --cov=dbt_skillz
```

## Project Structure

```
dbt_skillz/
├── __init__.py
├── cli.py              # CLI entry point (click)
├── compiler.py         # Orchestrator (parse → generate)
├── models.py           # Intermediate representation (IR)
├── parsers/
│   ├── base.py        # Abstract parser
│   └── dbt.py         # dbt project parser
├── generators/
│   ├── base.py        # Abstract generator
│   └── skill.py       # Markdown output generator
└── templates/         # Jinja2 templates
    ├── skill_main.md.j2
    ├── layer.md.j2
    ├── sources.md.j2
    ├── macros.md.j2
    └── lineage.md.j2

tests/
├── conftest.py        # pytest configuration
├── test_parser.py     # Parser tests
├── test_generator.py  # Generator tests
├── test_cli.py        # CLI tests
└── fixtures/
    └── basic_project/ # Sample dbt project for tests
```

## Making Changes

### Branching

Use descriptive branch names:

```bash
git checkout -b feature/add-json-output
git checkout -b fix/handle-disabled-models
git checkout -b docs/improve-readme
```

### Commits

Write clear commit messages:

```bash
git commit -m "Add support for disabled models in parser"
git commit -m "Fix type errors in compiler.py"
```

### Pull Requests

1. Push your branch to GitHub
2. Open a PR with a clear description
3. Ensure all CI checks pass
4. Request review from maintainers

### Coverage Requirements

- Aim for **80%+ code coverage** on new code
- All new features should include tests
- Run `pytest --cov` before submitting

## Release Process

### Version Bumping

Update `pyproject.toml`:

```toml
[project]
version = "0.2.0"  # Semantic versioning: MAJOR.MINOR.PATCH
```

### Creating a Release

1. Update `CHANGELOG.md` with new features/fixes
2. Commit version bump and changelog
3. Create a git tag: `git tag v0.2.0`
4. Push tag: `git push origin v0.2.0`
5. GitHub Actions automatically publishes to PyPI

### Changelog Format

```markdown
## [0.2.0] - 2024-03-15

### Added
- Support for dbt 1.6+
- `--include-sql` flag for SQL snippets

### Fixed
- Handle disabled models correctly
- Type errors in compiler

### Changed
- Renamed `ClaudeSkillGenerator` to `SkillGenerator`
```

## Code Style

- **Line length**: 100 characters
- **Formatting**: `ruff format`
- **Linting**: `ruff check`
- **Type hints**: Use `from __future__ import annotations` and full type hints
- **Docstrings**: Google-style docstrings

## Questions?

Open an issue on GitHub or reach out to the maintainers.

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.
