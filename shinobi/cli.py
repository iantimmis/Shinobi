"""Shinobi CLI - Enhanced project initialization tool built on top of uv."""

import subprocess
from pathlib import Path
from typing import Optional

import questionary
import typer
from rich.console import Console
from rich.prompt import Confirm

app = typer.Typer()
console = Console()


def run_command(command: list[str], cwd: Optional[Path] = None) -> None:
    """Run a shell command and handle errors."""
    # Replace pip commands with uv pip to ensure we use uv
    if command[0] == "pip":
        command = ["uv", "pip"] + command[1:]
    elif command[0] == "python" and command[1] == "-m" and command[2] == "pip":
        command = ["uv", "pip"] + command[3:]

    try:
        subprocess.run(command, check=True, cwd=cwd)
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Error running command: {' '.join(command)}[/red]")
        raise typer.Exit(1) from e


def setup_ruff(project_path: Path) -> None:
    """Set up Ruff configuration and pre-commit hook."""
    # Create .pre-commit-config.yaml
    pre_commit_config = """repos:
-   repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.3.0
    hooks:
    -   id: ruff
        args: [--fix]
    -   id: ruff-format
"""
    (project_path / ".pre-commit-config.yaml").write_text(pre_commit_config)

    # Add pre-commit to the development dependencies and configure Ruff
    # Modify pyproject.toml to include pre-commit in the dev dependencies and Ruff config
    pyproject_path = project_path / "pyproject.toml"
    if pyproject_path.exists():
        content = pyproject_path.read_text()

        # Check if dev dependencies section exists
        if "[dependency-groups]" not in content:
            # Add dev dependencies section with pre-commit and ruff
            dev_section = """
[dependency-groups]
dev = [
    "pre-commit>=3.0.0",
    "ruff>=0.3.0",
]
"""
            # Find the right spot to insert it (after [project] section)
            if "[build-system]" in content:
                content = content.replace(
                    "[build-system]", dev_section + "\n[build-system]"
                )
            else:
                content += dev_section

        # Check if pre-commit and ruff are already in dev dependencies
        elif "pre-commit" not in content or "ruff" not in content:
            # Insert pre-commit and ruff into existing dev dependencies
            import re

            dev_pattern = r"(\[dependency-groups\]\s*\ndev\s*=\s*\[(?:[^\]]*\n)?)(\])"
            if "pre-commit" not in content:
                content = re.sub(
                    dev_pattern, r'\1    "pre-commit>=3.0.0",\n\2', content
                )
            if "ruff" not in content:
                content = re.sub(dev_pattern, r'\1    "ruff>=0.3.0",\n\2', content)

        # Add Ruff configuration at the end of the file
        ruff_config = """
[tool.ruff]
line-length = 88
target-version = "py312"
fix = true

[tool.ruff.lint]
select = ["E", "F", "I"]
ignore = ["E501"]  # Example: ignore line length

[tool.ruff.format]
quote-style = "double"
"""
        content += ruff_config

        pyproject_path.write_text(content)

    console.print(
        "[yellow]Added pre-commit and ruff to dev dependencies. To install them, run:[/yellow]"
    )
    console.print(
        f"[green]cd {project_path} && uv pip install -e '.[dev]' && pre-commit install[/green]"
    )


def setup_github_workflows(project_path: Path) -> None:
    """Set up GitHub Actions workflows for linting and testing."""
    workflows_dir = project_path / ".github" / "workflows"
    workflows_dir.mkdir(parents=True, exist_ok=True)

    # Lint workflow
    lint_workflow = """name: Ruff Lint

on: [push, pull_request]

jobs:
  ruff:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/ruff-action@v3
        with:
          version: latest
"""
    (workflows_dir / "lint.yml").write_text(lint_workflow)

    # Test workflow
    test_workflow = """name: Test

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - uses: actions/setup-python@v5
      with:
        python-version: '3.11'
    - name: Install uv
      run: |
        curl -LsSf https://astral.sh/uv/install.sh | sh
        echo "$HOME/.cargo/bin" >> $GITHUB_PATH
    - name: Install dependencies
      run: |
        uv pip install -e ".[dev]"
    - name: Run tests
      run: pytest
"""
    (workflows_dir / "test.yml").write_text(test_workflow)


def create_vscode_settings(project_path: Path) -> None:
    """Create VS Code settings.json file."""
    vscode_dir = project_path / ".vscode"
    vscode_dir.mkdir(exist_ok=True)

    settings_content = """{
    "[python]": {
      "editor.formatOnSave": true,
      "editor.codeActionsOnSave": {
        "source.fixAll": "explicit",
        "source.organizeImports": "explicit"
      },
      "editor.defaultFormatter": "charliermarsh.ruff"
    }
  }"""
    (vscode_dir / "settings.json").write_text(settings_content)


def create_cursor_rules(project_path: Path) -> None:
    """Create Cursor rules file."""
    cursor_dir = project_path / ".cursor" / "rules"
    cursor_dir.mkdir(parents=True, exist_ok=True)

    rules_content = """---
description: Always Use UV for Python
globs: 
alwaysApply: true
---
# Always Use UV for Python

This project uses `uv` as the Python package manager and environment tool. Follow these guidelines:

## Package Management

- To add new dependencies:
  ```bash
  uv add package_name
  ```

- To update the environment with dependencies from requirements.txt:
  ```bash
  uv sync
  ```

## Running Python Code

- Always use `uv run` to execute Python files:
  ```bash
  uv run myfile.py
  ```

## Benefits of UV

- Faster than pip
- Better dependency resolution
- Built-in virtual environment management

## Common Commands

- Install a package: `uv add package_name`
- Update or install dependencies: `uv sync`
- Run Python file: `uv run file.py`
- Create new venv: `uv venv`
"""
    (cursor_dir / "use-uv-always.mdc").write_text(rules_content)


def validate_project_name(name: str) -> tuple[bool, str]:
    """Validate project name according to Python package naming rules.

    Rules:
    - Must start and end with a letter or digit
    - May only contain -, _, ., and alphanumeric characters
    """
    import re

    if not name:
        return False, "Project name cannot be empty"

    # Check if starts and ends with letter/digit
    if not (name[0].isalnum() and name[-1].isalnum()):
        return False, "Project name must start and end with a letter or digit"

    # Check if contains only allowed characters
    if not re.match(r"^[a-zA-Z0-9][a-zA-Z0-9._-]*[a-zA-Z0-9]$", name):
        return False, "Project name may only contain letters, digits, '-', '_', and '.'"

    return True, ""


def get_project_config() -> Optional[dict]:
    """Get project configuration through interactive prompts."""
    console.print(
        "\n[bold blue]Welcome to Shinobi! Let's set up your project.[/bold blue]\n"
    )

    try:
        # Get project name with validation
        while True:
            project_name = questionary.text(
                "What's the name of your project?",
                validate=lambda text: len(text) > 0,
            ).ask()

            if project_name is None:  # User pressed Ctrl+C
                return None

            is_valid, error_msg = validate_project_name(project_name)
            if is_valid:
                break

            console.print(f"[red]Invalid project name: {error_msg}[/red]")
            console.print("[yellow]Project names must:[/yellow]")
            console.print("- Start and end with a letter or digit")
            console.print("- May only contain letters, digits, '-', '_', and '.'")
            console.print("Please try again.\n")

        # Get project description
        description = questionary.text(
            "What's the description of your project?",
            default="",
        ).ask()

        if description is None:  # User pressed Ctrl+C
            return None

        # Get Python version
        python_version = questionary.select(
            "Which Python version would you like to use?",
            choices=["3.13", "3.12", "3.11"],
            default="3.13",
        ).ask()

        if python_version is None:  # User pressed Ctrl+C
            return None

        # Get IDE preference
        ide = questionary.select(
            "Which IDE are you using?",
            choices=["Cursor", "VS Code", "Other"],
            default="VS Code",
        ).ask()

        if ide is None:  # User pressed Ctrl+C
            return None

        # Get additional features
        features = questionary.checkbox(
            "Select additional features to include:",
            choices=[
                {
                    "name": "GitHub Actions",
                    "value": "github",
                    "checked": True,
                    "description": "Set up GitHub Actions workflows for linting and testing",
                },
                {
                    "name": "Pre-commit hooks",
                    "value": "precommit",
                    "checked": True,
                    "description": "Set up pre-commit hooks for Ruff",
                },
                {
                    "name": "Pytest",
                    "value": "pytest",
                    "checked": True,
                    "description": "Set up pytest for testing",
                },
            ],
        ).ask()

        if features is None:  # User pressed Ctrl+C
            return None

        return {
            "project_name": project_name,
            "description": description,
            "python_version": python_version,
            "ide": ide,
            "features": features,
        }
    except KeyboardInterrupt:
        return None


def create_readme(project_path: Path, config: dict) -> None:
    """Create a comprehensive README.md file for the project."""
    readme_content = f"""<div align="center">
<h1> {config["project_name"]} </h1>

{config["description"] or "A Python project initialized with Shinobi."}

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
"""
    (project_path / "README.md").write_text(readme_content)


def create_license(project_path: Path) -> None:
    """Create an MIT license file for the project."""
    from datetime import datetime

    current_year = datetime.now().year

    license_content = f"""MIT License

Copyright (c) {current_year}

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
    (project_path / "LICENSE").write_text(license_content)


def update_pyproject_description(pyproject_path: Path, description: str) -> None:
    """Update the project description in pyproject.toml."""
    if not description:
        return

    if pyproject_path.exists():
        content = pyproject_path.read_text()

        # Escape quotes and handle multiline descriptions
        escaped_description = description.replace('"', '\\"').replace("\n", "\\n")

        # Try to replace empty description first
        if 'description = ""' in content:
            content = content.replace(
                'description = ""', f'description = "{escaped_description}"'
            )
        # If no empty description, try to replace existing one
        elif 'description = "' in content:
            import re

            content = re.sub(
                r'description = "[^"]*"',
                f'description = "{escaped_description}"',
                content,
            )
        # If no description field exists, add it after the name field
        else:
            content = content.replace(
                'name = "', f'name = "\ndescription = "{escaped_description}"'
            )

        pyproject_path.write_text(content)


def create_gitignore(project_path: Path) -> None:
    """Create a comprehensive .gitignore file for Python projects."""
    gitignore_content = (
        "# Created by https://www.toptal.com/developers/gitignore/api/python\n"
        "# Edit at https://www.toptal.com/developers/gitignore?templates=python\n\n"
        "### Python ###\n"
        "# Byte-compiled / optimized / DLL files\n"
        "__pycache__/\n"
        "*.py[cod]\n"
        "*$py.class\n\n"
        "# C extensions\n"
        "*.so\n\n"
        "# Distribution / packaging\n"
        ".Python\n"
        "build/\n"
        "develop-eggs/\n"
        "dist/\n"
        "downloads/\n"
        "eggs/\n"
        ".eggs/\n"
        "lib/\n"
        "lib64/\n"
        "parts/\n"
        "sdist/\n"
        "var/\n"
        "wheels/\n"
        "share/python-wheels/\n"
        "*.egg-info/\n"
        ".installed.cfg\n"
        "*.egg\n"
        "MANIFEST\n\n"
        "# PyInstaller\n"
        "#  Usually these files are written by a python script from a template\n"
        "#  before PyInstaller builds the exe, so as to inject date/other infos into it.\n"
        "*.manifest\n"
        "*.spec\n\n"
        "# Installer logs\n"
        "pip-log.txt\n"
        "pip-delete-this-directory.txt\n\n"
        "# Unit test / coverage reports\n"
        "htmlcov/\n"
        ".tox/\n"
        ".nox/\n"
        ".coverage\n"
        ".coverage.*\n"
        ".cache\n"
        "nosetests.xml\n"
        "coverage.xml\n"
        "*.cover\n"
        "*.py,cover\n"
        ".hypothesis/\n"
        ".pytest_cache/\n"
        "cover/\n\n"
        "# Translations\n"
        "*.mo\n"
        "*.pot\n\n"
        "# Django stuff:\n"
        "*.log\n"
        "local_settings.py\n"
        "db.sqlite3\n"
        "db.sqlite3-journal\n\n"
        "# Flask stuff:\n"
        "instance/\n"
        ".webassets-cache\n\n"
        "# Scrapy stuff:\n"
        ".scrapy\n\n"
        "# Sphinx documentation\n"
        "docs/_build/\n\n"
        "# PyBuilder\n"
        ".pybuilder/\n"
        "target/\n\n"
        "# Jupyter Notebook\n"
        ".ipynb_checkpoints\n\n"
        "# IPython\n"
        "profile_default/\n"
        "ipython_config.py\n\n"
        "# pyenv\n"
        "#   For a library or package, you might want to ignore these files since the code is\n"
        "#   intended to run in multiple environments; otherwise, check them in:\n"
        "# .python-version\n\n"
        "# pipenv\n"
        "#   According to pypa/pipenv#598, it is recommended to include Pipfile.lock in version control.\n"
        "#   However, in case of collaboration, if having platform-specific dependencies or dependencies\n"
        "#   having no cross-platform support, pipenv may install dependencies that don't work, or not\n"
        "#   install all needed dependencies.\n"
        "#Pipfile.lock\n\n"
        "# poetry\n"
        "#   Similar to Pipfile.lock, it is generally recommended to include poetry.lock in version control.\n"
        "#   This is especially recommended for binary packages to ensure reproducibility, and is more\n"
        "#   commonly ignored for libraries.\n"
        "#   https://python-poetry.org/docs/basic-usage/#commit-your-poetrylock-file-to-version-control\n"
        "#poetry.lock\n\n"
        "# pdm\n"
        "#   Similar to Pipfile.lock, it is generally recommended to include pdm.lock in version control.\n"
        "#pdm.lock\n"
        "#   pdm stores project-wide configurations in .pdm.toml, but it is recommended to not include it\n"
        "#   in version control.\n"
        "#   https://pdm.fming.dev/#use-with-ide\n"
        ".pdm.toml\n\n"
        "# PEP 582; used by e.g. github.com/David-OConnor/pyflow and github.com/pdm-project/pdm\n"
        "__pypackages__/\n\n"
        "# Celery stuff\n"
        "celerybeat-schedule\n"
        "celerybeat.pid\n\n"
        "# SageMath parsed files\n"
        "*.sage.py\n\n"
        "# Environments\n"
        ".env\n"
        ".venv\n"
        "env/\n"
        "venv/\n"
        "ENV/\n"
        "env.bak/\n"
        "venv.bak/\n\n"
        "# Spyder project settings\n"
        ".spyderproject\n"
        ".spyproject\n\n"
        "# Rope project settings\n"
        ".ropeproject\n\n"
        "# mkdocs documentation\n"
        "/site\n\n"
        "# mypy\n"
        ".mypy_cache/\n"
        ".dmypy.json\n"
        "dmypy.json\n\n"
        "# Pyre type checker\n"
        ".pyre/\n\n"
        "# pytype static type analyzer\n"
        ".pytype/\n\n"
        "# Cython debug symbols\n"
        "cython_debug/\n\n"
        "# PyCharm\n"
        "#  JetBrains specific template is maintained in a separate JetBrains.gitignore that can\n"
        "#  be found at https://github.com/github/gitignore/blob/main/Global/JetBrains.gitignore\n"
        "#  and can be added to the global gitignore or merged into this file.  For a more nuclear\n"
        "#  option (not recommended) you can uncomment the following to ignore the entire idea folder.\n"
        "#.idea/\n\n"
        "### Python Patch ###\n"
        "# Poetry local configuration file - https://python-poetry.org/docs/configuration/#local-configuration\n"
        "poetry.toml\n\n"
        "# ruff\n"
        ".ruff_cache/\n\n"
        "# LSP config files\n"
        "pyrightconfig.json\n\n"
        "# End of https://www.toptal.com/developers/gitignore/api/python"
    )
    (project_path / ".gitignore").write_text(gitignore_content)


@app.command()
def init() -> None:
    """Initialize a new Python project with enhanced features."""
    config = get_project_config()
    if config is None:
        console.print("\n[yellow]Operation cancelled by user.[/yellow]")
        raise typer.Exit(0)

    project_path = Path(config["project_name"])

    if project_path.exists():
        if not Confirm.ask(
            f"Directory {config['project_name']} already exists. Continue?"
        ):
            raise typer.Exit()

    # Run uv init
    console.print("\n[yellow]Running uv init...[/yellow]")
    run_command(["uv", "init", config["project_name"]])

    # Move hello.py to main.py if it exists
    hello_py = project_path / "hello.py"
    if hello_py.exists():
        hello_py.rename(project_path / "main.py")

    # Create src directory and move main.py into it
    src_dir = project_path / "src"
    src_dir.mkdir(exist_ok=True)
    main_py = project_path / "main.py"
    if main_py.exists():
        main_py.rename(src_dir / "main.py")

    # Create tests directory
    tests_dir = project_path / "tests"
    tests_dir.mkdir(exist_ok=True)
    (tests_dir / "__init__.py").touch()

    # Create .gitignore
    create_gitignore(project_path)

    # Set up features based on selection
    if "precommit" in config["features"]:
        console.print("[yellow]Setting up Ruff and pre-commit hooks...[/yellow]")
        setup_ruff(project_path)

    if "github" in config["features"]:
        console.print("[yellow]Setting up GitHub workflows...[/yellow]")
        setup_github_workflows(project_path)

    if "pytest" in config["features"]:
        console.print("[yellow]Setting up pytest...[/yellow]")
        # Add pytest to dev dependencies in pyproject.toml
        pyproject_path = project_path / "pyproject.toml"
        if pyproject_path.exists():
            content = pyproject_path.read_text()

            # Check if dev dependencies section exists
            if "[dependency-groups]" not in content:
                # Add dev dependencies section with pytest
                dev_section = """
[dependency-groups]
dev = [
    "pytest>=7.0.0",
]
"""
                # Find the right spot to insert it (after [project] section)
                if "[build-system]" in content:
                    content = content.replace(
                        "[build-system]", dev_section + "\n[build-system]"
                    )
                else:
                    content += dev_section

            # Check if pytest is already in dev dependencies
            elif "pytest" not in content:
                # Insert pytest into existing dev dependencies
                import re

                dev_pattern = (
                    r"(\[dependency-groups\]\s*\ndev\s*=\s*\[(?:[^\]]*\n)?)(\])"
                )
                content = re.sub(dev_pattern, r'\1    "pytest>=7.0.0",\n\2', content)

            pyproject_path.write_text(content)

        # Create a basic test file
        test_file = tests_dir / "test_main.py"
        test_file.write_text('''def test_example():
    """Example test."""
    assert True
''')

    # Update pyproject.toml with project description
    update_pyproject_description(project_path / "pyproject.toml", config["description"])

    # Create a comprehensive README.md
    create_readme(project_path, config)

    # Create LICENSE file
    create_license(project_path)

    # Set up IDE configuration
    if config["ide"] == "VS Code":
        create_vscode_settings(project_path)
    elif config["ide"] == "Cursor":
        create_vscode_settings(project_path)  # Cursor also uses VS Code settings
        create_cursor_rules(project_path)

    console.print("\n[green]Project initialized successfully![/green]")
    console.print("\nNext steps:")
    console.print(f"1. cd {config['project_name']}")
    console.print("2. Install dependencies: uv pip install -e '.[dev]'")
    if "precommit" in config["features"]:
        console.print("3. Set up pre-commit: pre-commit install")
    if "github" in config["features"]:
        console.print(
            "4. Initialize git repository: git init && git add . && git commit -m 'Initial commit'"
        )


if __name__ == "__main__":
    app()
