<div align="center">
<h1> {config["project_name"]} </h1>

{config["description"] or "A Python project initialized with Shinobi."}

</div>

---

## ✨ Features

### 🛠️ Project Structure

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

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/{config["project_name"]}.git
cd {config["project_name"]}

# Install dependencies
uv pip install -e '.[dev]'

# Set up pre-commit hooks (if enabled)
uv run pre-commit install
```

## Development

### Project Structure

```
{config["project_name"]}/
├── src/
│   └── main.py
├── tests/
│   └── __init__.py
├── .pre-commit-config.yaml
├── pyproject.toml
└── README.md
```

### Running Tests

```bash
pytest
```

### Code Quality

This project uses Ruff for linting and formatting. To run the checks:

```bash
# Lint
uvx ruff check

# Format
uvx ruff format
```

## License

[MIT License](LICENSE)
