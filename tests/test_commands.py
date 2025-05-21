"""Test cases for command execution."""

import subprocess
from unittest.mock import patch

import pytest
import typer

from shinobi.cli import run_command


def test_run_command_success():
    """Test successful command execution."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = subprocess.CompletedProcess([], 0)
        run_command(["echo", "test"])
        mock_run.assert_called_once()


def test_run_command_failure():
    """Test command execution failure."""
    with patch("subprocess.run") as mock_run:
        mock_run.side_effect = subprocess.CalledProcessError(1, ["echo", "test"])
        with pytest.raises(typer.Exit) as exc_info:
            run_command(["echo", "test"])
        assert exc_info.value.exit_code == 1


def test_run_command_pip_conversion():
    """Test pip command conversion to uv pip."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = subprocess.CompletedProcess([], 0)

        # Test direct pip command
        run_command(["pip", "install", "package"])
        mock_run.assert_called_with(
            ["uv", "pip", "install", "package"], check=True, cwd=None
        )

        # Test python -m pip command
        run_command(["python", "-m", "pip", "install", "package"])
        mock_run.assert_called_with(
            ["uv", "pip", "install", "package"], check=True, cwd=None
        )


def test_run_command_with_cwd():
    """Test command execution with working directory."""
    with patch("subprocess.run") as mock_run:
        mock_run.return_value = subprocess.CompletedProcess([], 0)
        run_command(["echo", "test"], cwd="/tmp")
        mock_run.assert_called_with(["echo", "test"], check=True, cwd="/tmp")
