<div align="center">
  <img src="images/shinobi.png" width="300">
  <p>Enhanced project initialization tool built on top of `uv`. Shinobi helps you set up Python projects with best practices and common tools pre-configured.</p>
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
git clone https://github.com/iantimmis/shinobi.git
cd shinobi

# Install dependencies
uv sync

# Set up pre-commit hooks (if enabled)
uv run pre-commit install
```

## Development

### Project Structure

```
shinobi/
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
uv run pytest
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
