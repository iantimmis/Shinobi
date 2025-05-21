"""Test cases for the shinobi CLI."""

import os
from pathlib import Path
from unittest.mock import patch

import pytest
from typer.testing import CliRunner

from shinobi.cli import app
from shinobi.cli import init as cli_init_func


@pytest.fixture
def runner():
    """Create a CLI runner for testing."""
    return CliRunner()


def test_cli_help(runner):
    """Test that the CLI shows help text."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Shinobi - Enhanced Python project initialization tool" in result.stdout
    assert "init" in result.stdout


def test_cli_init_help(runner):
    """Test that the init command shows help text."""
    result = runner.invoke(app, ["init", "--help"])
    assert result.exit_code == 0
    assert "Initialize a new Python project" in result.stdout


def test_cli_init_basic(tmp_path):  # Removed runner
    """Test basic project initialization by calling init() directly."""
    with patch("shinobi.cli.get_project_config") as mock_config:
        mock_config.return_value = {
            "project_name": "test-project",
            "description": "A test project",
            "python_version": "3.11",
            "ide": "VS Code",
            "features": ["precommit", "github", "pytest"],
            "github_owner": "testuser",
            "github_repo": "test-project",
        }
        project_name_val = mock_config.return_value["project_name"]

        # Create the main project directory first
        main_project_dir = tmp_path / project_name_val
        main_project_dir.mkdir()

        # Create a dummy pyproject.toml that 'uv init' would have created
        dummy_pyproject_content = f"""
[project]
name = "{project_name_val}"
version = "0.1.0"
description = ""
requires-python = ">=3.8"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
"""
        (main_project_dir / "pyproject.toml").write_text(dummy_pyproject_content)

        with (
            patch("shinobi.cli.run_command") as mock_run,
            patch("shinobi.cli.Confirm.ask") as mock_confirm_ask,
        ):
            mock_confirm_ask.return_value = (
                True  # Ensure Confirm.ask doesn't try to read stdin
            )
            original_cwd = Path.cwd()
            try:
                os.chdir(
                    tmp_path
                )  # shinobi.cli.init() expects to be in the parent of project_name_val
                # Call the init function directly
                cli_init_func()
            finally:
                os.chdir(original_cwd)

            # Check that uv init was called with correct project name relative to tmp_path
            # The init command creates the project dir inside the CWD (which is tmp_path)
            mock_run.assert_any_call(["uv", "init", project_name_val])

            # Check that project structure was created relative to tmp_path
            created_project_path = tmp_path / project_name_val
            assert created_project_path.is_dir()
            assert (created_project_path / "src").is_dir()
            assert (created_project_path / "tests").is_dir()
            assert (created_project_path / "pyproject.toml").is_file()
            assert (created_project_path / "README.md").is_file()
            assert (created_project_path / "LICENSE").is_file()

            # Check that GitHub workflows were created
            assert (
                created_project_path / ".github" / "workflows" / "lint.yml"
            ).is_file()
            assert (
                created_project_path / ".github" / "workflows" / "test.yml"
            ).is_file()

            # Check that VS Code settings were created
            assert (created_project_path / ".vscode" / "settings.json").is_file()

            # Check README content
            readme_content = (created_project_path / "README.md").read_text()
            assert "[![Unit Tests]" in readme_content
            assert "https://github.com/testuser/test-project" in readme_content
