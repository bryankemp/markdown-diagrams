"""Tests for the markdown_diagrams CLI (main module)."""

from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from markdown_diagrams.main import cli

DATA_DIR = Path(__file__).parent / "data"


@pytest.fixture
def runner():
    return CliRunner()


class TestCLI:
    """Tests for the top-level CLI group."""

    def test_help(self, runner):
        result = runner.invoke(cli, ["--help"])
        assert result.exit_code == 0
        assert "Extract and render diagrams" in result.output

    def test_extract_help(self, runner):
        result = runner.invoke(cli, ["extract", "--help"])
        assert result.exit_code == 0
        assert "--output-dir" in result.output
        assert "--format" in result.output


class TestExtractCommand:
    """Tests for the 'extract' subcommand."""

    @patch("markdown_diagrams.main._check_external_tools")
    @patch("markdown_diagrams.main.render_mermaid_diagram")
    def test_extract_simple_file(self, mock_render, mock_check, runner):
        """Extract from a real fixture, mocking only the renderer."""
        mock_render.return_value = "/tmp/diagram.png"
        result = runner.invoke(cli, ["extract", str(DATA_DIR / "simple_flowchart.md")])
        assert result.exit_code == 0
        assert "Found 1 diagrams total" in result.output
        assert mock_render.called

    @patch("markdown_diagrams.main._check_external_tools")
    @patch("markdown_diagrams.main.render_mermaid_diagram")
    def test_extract_multiple_diagrams(self, mock_render, mock_check, runner):
        mock_render.return_value = "/tmp/diagram.png"
        result = runner.invoke(cli, ["extract", str(DATA_DIR / "multiple_diagrams.md")])
        assert result.exit_code == 0
        assert "Found 3 diagrams total" in result.output

    @patch("markdown_diagrams.main._check_external_tools")
    def test_extract_no_diagrams(self, mock_check, runner):
        result = runner.invoke(cli, ["extract", str(DATA_DIR / "no_diagrams.md")])
        assert result.exit_code == 0
        assert "Found 0 diagrams total" in result.output

    def test_extract_nonexistent_file(self, runner):
        result = runner.invoke(cli, ["extract", "/tmp/nonexistent_12345.md"])
        assert result.exit_code != 0

    @patch("markdown_diagrams.main._check_external_tools")
    @patch("markdown_diagrams.main.render_mermaid_diagram")
    def test_extract_with_output_dir(self, mock_render, mock_check, runner, tmp_path):
        mock_render.return_value = str(tmp_path / "out.png")
        result = runner.invoke(
            cli,
            [
                "extract",
                str(DATA_DIR / "simple_flowchart.md"),
                "-o",
                str(tmp_path),
            ],
        )
        assert result.exit_code == 0

    @patch("markdown_diagrams.main._check_external_tools")
    @patch("markdown_diagrams.main.render_mermaid_diagram")
    def test_extract_render_failure(self, mock_render, mock_check, runner):
        """When the renderer returns None, the CLI reports failure."""
        mock_render.return_value = None
        result = runner.invoke(cli, ["extract", str(DATA_DIR / "simple_flowchart.md")])
        assert result.exit_code == 0
        assert "Failed to render" in result.output
