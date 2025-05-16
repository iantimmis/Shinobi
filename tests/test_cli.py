"""Test cases for the shinobi CLI."""

from typer.testing import CliRunner

from shinobi.cli import app


def test_cli_help():
    """Test that the CLI shows help text."""
    runner = CliRunner()
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage" in result.stdout
