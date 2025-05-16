"""Test cases for project configuration."""

from unittest.mock import patch

import pytest
from questionary import Question

from shinobi.cli import get_project_config


@pytest.fixture
def mock_questionary():
    """Mock questionary responses."""
    with patch("shinobi.cli.questionary") as mock:
        # Mock text input for project name
        mock.text.return_value = Question.ask = lambda: "test-project"

        # Mock text input for description
        mock.text.return_value = Question.ask = lambda: "A test project"

        # Mock select for Python version
        mock.select.return_value = Question.ask = lambda: "3.11"

        # Mock select for IDE
        mock.select.return_value = Question.ask = lambda: "VS Code"

        # Mock checkbox for features
        mock.checkbox.return_value = Question.ask = lambda: [
            "precommit",
            "github",
            "pytest",
        ]

        yield mock


def test_get_project_config(mock_questionary):
    """Test project configuration gathering."""
    config = get_project_config()

    assert config["project_name"] == "test-project"
    assert config["description"] == "A test project"
    assert config["python_version"] == "3.11"
    assert config["ide"] == "VS Code"
    assert config["features"] == ["precommit", "github", "pytest"]

    # Verify questionary calls
    mock_questionary.text.assert_called()
    mock_questionary.select.assert_called()
    mock_questionary.checkbox.assert_called()


def test_get_project_config_minimal(mock_questionary):
    """Test project configuration with minimal features."""
    # Override checkbox response
    mock_questionary.checkbox.return_value = Question.ask = lambda: []

    config = get_project_config()

    assert config["project_name"] == "test-project"
    assert config["description"] == "A test project"
    assert config["python_version"] == "3.11"
    assert config["ide"] == "VS Code"
    assert config["features"] == []


def test_get_project_config_cursor_ide(mock_questionary):
    """Test project configuration with Cursor IDE."""
    # Override IDE selection
    mock_questionary.select.return_value = Question.ask = lambda: "Cursor"

    config = get_project_config()

    assert config["ide"] == "Cursor"
    assert config["features"] == ["precommit", "github", "pytest"]
