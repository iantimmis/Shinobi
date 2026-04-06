"""End-to-end integration tests for project initialization."""

import pytest

from shinobi.commands.init import initialize_project


def _make_config(
    name: str,
    *,
    description: str = "A test project",
    python_version: str = "3.13",
    ide: str = "VS Code",
    features: list[str] | None = None,
    github_owner: str = "",
    github_repo: str = "",
) -> dict:
    if features is None:
        features = ["precommit", "github"]
    github_url = (
        f"https://github.com/{github_owner}/{github_repo}" if github_owner else ""
    )
    return {
        "project_name": name,
        "description": description,
        "python_version": python_version,
        "python_version_nodot": python_version.replace(".", ""),
        "ide": ide,
        "features": features,
        "github_url": github_url,
        "github_owner": github_owner,
        "github_repo": github_repo,
    }


@pytest.mark.integration
def test_initialize_full_features(tmp_path):
    """Full init with precommit, github workflows, and VS Code IDE."""
    config = _make_config(
        "full-project",
        github_owner="testowner",
        github_repo="full-project",
    )
    initialize_project(config, base_dir=tmp_path)

    project = tmp_path / "full-project"

    # Core structure
    assert (project / "src" / "main.py").exists()
    assert (project / "tests" / "__init__.py").exists()
    assert (project / "tests" / "test_main.py").exists()
    assert (project / ".gitignore").exists()

    # pyproject.toml content
    pyproject = (project / "pyproject.toml").read_text()
    assert "[tool.pytest.ini_options]" in pyproject
    assert '"pytest' in pyproject
    assert "A test project" in pyproject

    # Pre-commit / ruff (feature: precommit)
    assert (project / ".pre-commit-config.yaml").exists()
    assert "[tool.ruff]" in pyproject

    # GitHub workflows (feature: github)
    assert (project / ".github" / "workflows" / "lint.yml").exists()
    assert (project / ".github" / "workflows" / "test.yml").exists()

    # VS Code IDE settings
    assert (project / ".vscode" / "settings.json").exists()
    assert (project / ".vscode" / "extensions.json").exists()

    # Always-generated files
    assert (project / "AGENTS.md").exists()

    readme = (project / "README.md").read_text()
    assert "full-project" in readme
    assert "testowner" in readme

    license_text = (project / "LICENSE").read_text()
    assert "MIT License" in license_text


@pytest.mark.integration
def test_initialize_minimal(tmp_path):
    """Minimal init with no optional features and 'Other' IDE."""
    config = _make_config("minimal-project", ide="Other", features=[])
    initialize_project(config, base_dir=tmp_path)

    project = tmp_path / "minimal-project"

    # Core structure still present
    assert (project / "src" / "main.py").exists()
    assert (project / "tests" / "__init__.py").exists()
    assert (project / "tests" / "test_main.py").exists()
    assert (project / ".gitignore").exists()
    assert (project / "AGENTS.md").exists()
    assert (project / "README.md").exists()
    assert (project / "LICENSE").exists()

    pyproject = (project / "pyproject.toml").read_text()
    assert "[tool.pytest.ini_options]" in pyproject

    # No optional features
    assert not (project / ".pre-commit-config.yaml").exists()
    assert not (project / ".github").exists()
    assert not (project / ".vscode").exists()


@pytest.mark.integration
def test_initialize_cursor_with_precommit(tmp_path):
    """Cursor IDE with precommit only (no github workflows)."""
    config = _make_config("cursor-project", ide="Cursor", features=["precommit"])
    initialize_project(config, base_dir=tmp_path)

    project = tmp_path / "cursor-project"

    # Core structure
    assert (project / "src" / "main.py").exists()
    assert (project / "tests" / "__init__.py").exists()

    # Cursor gets VS Code settings too
    assert (project / ".vscode" / "settings.json").exists()

    # Pre-commit present, workflows absent
    assert (project / ".pre-commit-config.yaml").exists()
    assert not (project / ".github").exists()

    # AGENTS.md always present
    assert (project / "AGENTS.md").exists()
