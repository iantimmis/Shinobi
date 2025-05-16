<div align="center">
<h1> Shinobi </h1>

Enhanced project initialization tool built on top of `uv`. Shinobi helps you set up Python projects with best practices and common tools pre-configured.

</div>

---

## Features

- Built on top of `uv init` for fast dependency management
- Automatic setup of:
  - Ruff for linting and formatting
  - Pre-commit hooks for Ruff
  - Proper project structure with `src` layout
  - Tests directory with `pytest` setup
  - Main entry point as `main.py`
- Optional GitHub integration:
  - GitHub Actions workflows for linting
  - GitHub Actions workflows for testing

## Installation

```bash
pip install -e .
```

## Usage

Basic usage:

```bash
shinobi init my-project
```

With GitHub workflows:

```bash
shinobi init my-project --github
```

## Project Structure

After initialization, your project will have the following structure:

```
my-project/
├── src/
│   └── main.py
├── tests/
│   └── __init__.py
├── .pre-commit-config.yaml
├── pyproject.toml
└── README.md
```

If using GitHub integration, it will also include:

```
my-project/
└── .github/
    └── workflows/
        ├── lint.yml
        └── test.yml
```

## Development

To contribute to Shinobi:

1. Clone the repository
2. Install development dependencies: `pip install -e ".[dev]"`
3. Make your changes
4. Run tests: `pytest`
5. Submit a pull request
