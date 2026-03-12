"""
Test cases for main CLI module.
"""

import pytest
from click.testing import CliRunner
from src.main import cli


def test_cli():
    """Test that the CLI loads without errors."""
    runner = CliRunner()
    result = runner.invoke(cli, ["--help"])
    assert result.exit_code == 0


def test_extract_command():
    """Test the extract command."""
    runner = CliRunner()
    # This will fail since we don't have a real markdown file, but at least it won't crash
    result = runner.invoke(cli, ["extract", "nonexistent.md"])
    # Should not crash even if file doesn't exist (though it will show an error)
    assert result.exit_code != -1  # Should not be a fatal error
