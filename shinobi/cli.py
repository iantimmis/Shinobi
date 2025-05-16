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

    # Add pre-commit to the development dependencies
    # Modify pyproject.toml to include pre-commit in the dev dependencies
    pyproject_path = project_path / "pyproject.toml"
    if pyproject_path.exists():
        content = pyproject_path.read_text()

        # Check if dev dependencies section exists
        if "[dependency-groups]" not in content:
            # Add dev dependencies section with pre-commit
            dev_section = """
[dependency-groups]
dev = [
    "pre-commit>=3.0.0",
]
"""
            # Find the right spot to insert it (after [project] section)
            if "[build-system]" in content:
                content = content.replace(
                    "[build-system]", dev_section + "\n[build-system]"
                )
            else:
                content += dev_section

        # Check if pre-commit is already in dev dependencies
        elif "pre-commit" not in content:
            # Insert pre-commit into existing dev dependencies
            import re

            dev_pattern = r"(\[dependency-groups\]\s*\ndev\s*=\s*\[(?:[^\]]*\n)?)(\])"
            content = re.sub(dev_pattern, r'\1    "pre-commit>=3.0.0",\n\2', content)

        pyproject_path.write_text(content)

    console.print(
        "[yellow]Added pre-commit to dev dependencies. To install it, run:[/yellow]"
    )
    console.print(
        f"[green]cd {project_path} && uv pip install -e '.[dev]' && pre-commit install[/green]"  # noqa: E501
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

    rules_content = """# Always Use UV for Python

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
"""  # noqa: E501
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


def get_project_config() -> dict:
    """Get project configuration through interactive prompts."""
    console.print(
        "\n[bold blue]Welcome to Shinobi! Let's set up your project.[/bold blue]\n"
    )

    # Get project name with validation
    while True:
        project_name = questionary.text(
            "What's the name of your project?",
            validate=lambda text: len(text) > 0,
        ).ask()

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

    # Get Python version
    python_version = questionary.select(
        "Which Python version would you like to use?",
        choices=["3.11", "3.12"],
        default="3.11",
    ).ask()

    # Get IDE preference
    ide = questionary.select(
        "Which IDE are you using?",
        choices=["Cursor", "VS Code", "Other"],
        default="VS Code",
    ).ask()

    # Get additional features
    features = questionary.checkbox(
        "Select additional features to include:",
        choices=[
            {
                "name": "GitHub Actions",
                "value": "github",
                "checked": True,
                "description": "Set up GitHub Actions workflows for linting and testing",  # noqa: E501
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

    return {
        "project_name": project_name,
        "description": description,
        "python_version": python_version,
        "ide": ide,
        "features": features,
    }


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


@app.command()
def init() -> None:
    """Initialize a new Python project with enhanced features."""
    config = get_project_config()
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
    if config["description"]:
        pyproject_path = project_path / "pyproject.toml"
        if pyproject_path.exists():
            content = pyproject_path.read_text()
            content = content.replace(
                'description = ""', f'description = "{config["description"]}"'
            )
            pyproject_path.write_text(content)

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
            "4. Initialize git repository: git init && git add . && git commit -m 'Initial commit'"  # noqa: E501
        )


if __name__ == "__main__":
    app()
