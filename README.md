# Shinobi

<div align="center">
  <img src="images/shinobi.png" width="500">
  <p>Enhanced project initialization tool built on top of `uv`. Shinobi helps you set up Python projects with best practices and common tools pre-configured.</p>

[![Unit Tests](https://github.com/iantimmis/shinobi/actions/workflows/test.yml/badge.svg)](https://github.com/iantimmis/shinobi/actions/workflows/test.yml)
[![Ruff](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

</div>

Shinobi is an enhanced Python project initialization tool built on top of `uv`. It provides a streamlined way to create new Python projects with modern best practices and tooling.

## Installation

```bash
# Install Shinobi
uv pip install shinobi
```

## Usage

Shinobi provides a simple CLI interface for initializing new Python projects:

```bash
# Show help
shinobi

# Initialize a new project
shinobi init

# Show help for init command
shinobi init --help
```

When you run `shinobi init`, you'll be guided through an interactive setup process that includes:

1. Project name and description
2. GitHub repository details (optional)
3. Python version selection
4. IDE preference (VS Code or Cursor)
5. Additional features:
   - GitHub Actions workflows
   - Pre-commit hooks with Ruff
   - Pytest setup

## Features

- Modern Python project structure with `src` layout
- Comprehensive test suite with pytest
- Optimized Python `.gitignore` from Toptal
- MIT License template

### 📦 Dependency Management

- Fast and reliable dependency management with `uv`
- Development dependencies group for testing and linting
- Pre-commit hooks for automated checks

### 🧰 Code Quality

- Ruff for lightning-fast linting and formatting
- Pre-commit hooks for automated code quality checks
- GitHub Actions workflows for CI/CD

### 🎯 IDE Support

- VS Code configuration with Ruff integration
- Cursor IDE rules for UV usage
- Editor-agnostic project structure

### 🔧 Development Tools

- GitHub Actions workflows for:
  - Automated linting with Ruff
  - Automated testing with pytest
- Pre-commit hooks for:
  - Ruff linting
  - Ruff formatting

## Project Structure

```
project_name/
├── src/              # Source code directory
│   └── main.py      # Main application code
├── tests/           # Test directory
│   └── __init__.py
├── .github/         # GitHub Actions workflows
├── .vscode/         # VS Code settings
├── .cursor/         # Cursor rules
├── .pre-commit-config.yaml
├── pyproject.toml   # Project configuration
└── README.md
```

## Development

### Running Tests

```bash
uv run pytest
```

### Code Quality

This project uses Ruff for linting and formatting. To run the checks:

```bash
# Lint
uv run ruff check

# Format
uv run ruff format
```

## License

[MIT License](LICENSE)
