<div align="center">
<h1> test-project </h1>

This is my prjoect bro

</div>

---

## Features

- Modern Python project structure with `src` layout
- Dependency management with `uv`
- Code quality tools:
  - Ruff for linting and formatting
  - Pre-commit hooks for automated checks
- Testing with pytest
- GitHub Actions workflows for CI/CD

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/test-project.git
cd test-project

# Install dependencies
uv pip install -e '.[dev]'

# Set up pre-commit hooks (if enabled)
uv run pre-commit install
```

## Development

### Project Structure

```
test-project/
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
