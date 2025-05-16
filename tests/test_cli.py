"""Test cases for the shinobi CLI."""

from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from shinobi.cli import app


@pytest.fixture
def runner():
    """Create a CLI runner for testing."""
    return CliRunner()


def test_cli_help(runner):
    """Test that the CLI shows help text."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage" in result.stdout


def test_cli_init_help(runner):
    """Test that the init command shows help text."""
    result = runner.invoke(app, ["init", "--help"])
    assert result.exit_code == 0
    assert "Initialize a new Python project" in result.stdout


def test_cli_init_basic(runner, tmp_path):
    """Test basic project initialization."""
    with patch("shinobi.cli.get_project_config") as mock_config:
        mock_config.return_value = {
            "project_name": "test-project",
            "description": "A test project",
            "python_version": "3.11",
            "ide": "VS Code",
            "features": ["precommit", "github", "pytest"],
        }

        with patch("shinobi.cli.run_command") as mock_run:
            result = runner.invoke(app, ["init"])
            assert result.exit_code == 0

            # Check that uv init was called
            mock_run.assert_any_call(["uv", "init", "test-project"])

            # Check that project structure was created
            project_path = Path("test-project")
            assert project_path.exists()
            assert (project_path / "src").exists()
            assert (project_path / "tests").exists()
            assert (project_path / "pyproject.toml").exists()
            assert (project_path / "README.md").exists()
            assert (project_path / "LICENSE").exists()

            # Check that GitHub workflows were created
            assert (project_path / ".github" / "workflows" / "lint.yml").exists()
            assert (project_path / ".github" / "workflows" / "test.yml").exists()

            # Check that VS Code settings were created
            assert (project_path / ".vscode" / "settings.json").exists()

            # Clean up
            project_path.rmdir()
