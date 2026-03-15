"""Tests for the markdown_diagrams.validators module."""

import shutil
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from markdown_diagrams.main import cli
from markdown_diagrams.validators import (
    ValidationResult,
    _parse_mmdc_errors,
    _write_fixes,
    fix_diagram,
    validate_and_fix_diagrams,
    validate_diagram,
)

DATA_DIR = Path(__file__).parent / "data"

# ---------------------------------------------------------------------------
# fix_diagram
# ---------------------------------------------------------------------------


class TestFixDiagram:
    """Tests for the fix_diagram heuristic fixer."""

    def test_strips_trailing_whitespace(self):
        content = "graph TD   \n    A --> B   \n    B --> C"
        result = fix_diagram(content)
        for line in result.splitlines():
            assert line == line.rstrip()

    def test_normalizes_crlf(self):
        content = "graph TD\r\n    A --> B\r\n"
        result = fix_diagram(content)
        assert "\r" not in result

    def test_normalizes_bare_cr(self):
        content = "graph TD\r    A --> B\r"
        result = fix_diagram(content)
        assert "\r" not in result

    def test_strips_leading_trailing_blank_lines(self):
        content = "\n\ngraph TD\n    A --> B\n\n"
        result = fix_diagram(content)
        assert not result.startswith("\n")
        assert not result.endswith("\n")

    def test_quotes_parens_in_flowchart_labels(self):
        content = "flowchart TD\n    A[Start (Init)] --> B[End]"
        result = fix_diagram(content)
        assert '["Start (Init)"]' in result

    def test_quotes_parens_in_diamond_labels(self):
        content = "flowchart TD\n    B{Check (valid)?} --> C[OK]"
        result = fix_diagram(content)
        assert '{"Check (valid)?"}' in result

    def test_no_change_for_clean_diagram(self):
        content = "graph TD\n    A[Start] --> B[End]"
        assert fix_diagram(content) == content

    def test_idempotent(self):
        content = "flowchart TD   \n    A[foo(x)] --> B[OK]   "
        first = fix_diagram(content)
        second = fix_diagram(first)
        assert first == second

    def test_empty_string_returns_empty(self):
        assert fix_diagram("") == ""

    def test_sequence_diagram_unchanged(self):
        content = "sequenceDiagram\n    A->>B: call foo(x)"
        assert fix_diagram(content) == content


# ---------------------------------------------------------------------------
# _parse_mmdc_errors
# ---------------------------------------------------------------------------


class TestParseMmdcErrors:
    """Tests for the mmdc stderr parser."""

    def test_detects_error_prefix(self):
        stderr = "Error: Parse error on line 3\nSome other output"
        errors = _parse_mmdc_errors(stderr)
        assert len(errors) == 1
        assert "Error" in errors[0]

    def test_detects_parse_error(self):
        errors = _parse_mmdc_errors("something: parse error near token X")
        assert errors

    def test_detects_syntax_error(self):
        errors = _parse_mmdc_errors("Syntax error at line 5")
        assert errors

    def test_detects_unexpected(self):
        errors = _parse_mmdc_errors("Unexpected token 'foo'")
        assert errors

    def test_ignores_unrelated_lines(self):
        stderr = "Generating diagram...\nDone."
        assert _parse_mmdc_errors(stderr) == []

    def test_empty_stderr(self):
        assert _parse_mmdc_errors("") == []

    def test_blank_lines_ignored(self):
        stderr = "\n   \nError: something bad\n\n"
        errors = _parse_mmdc_errors(stderr)
        assert len(errors) == 1


# ---------------------------------------------------------------------------
# validate_diagram
# ---------------------------------------------------------------------------


class TestValidateDiagram:
    """Tests for the mmdc-based diagram validator."""

    @patch("markdown_diagrams.validators.check_dependency")
    def test_mmdc_not_available_returns_valid(self, mock_dep):
        mock_dep.return_value = MagicMock(available=False)
        valid, errors = validate_diagram("graph TD\n    A --> B")
        assert valid is True
        assert errors == []

    @patch("markdown_diagrams.validators.check_dependency")
    @patch("markdown_diagrams.validators.subprocess.run")
    def test_mmdc_success_returns_valid(self, mock_run, mock_dep):
        mock_dep.return_value = MagicMock(available=True)
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        valid, errors = validate_diagram("graph TD\n    A --> B")
        assert valid is True
        assert errors == []

    @patch("markdown_diagrams.validators.check_dependency")
    @patch("markdown_diagrams.validators.subprocess.run")
    def test_mmdc_failure_returns_invalid(self, mock_run, mock_dep):
        mock_dep.return_value = MagicMock(available=True)
        mock_run.return_value = MagicMock(
            returncode=1, stderr="Error: Parse error on line 2"
        )
        valid, errors = validate_diagram("graph TD\n    ??? bad syntax")
        assert valid is False
        assert any("Parse error" in e for e in errors)

    @patch("markdown_diagrams.validators.check_dependency")
    @patch("markdown_diagrams.validators.subprocess.run")
    def test_mmdc_failure_no_stderr_uses_fallback(self, mock_run, mock_dep):
        mock_dep.return_value = MagicMock(available=True)
        mock_run.return_value = MagicMock(returncode=1, stderr="")
        valid, errors = validate_diagram("bad")
        assert valid is False
        assert errors  # fallback message present

    @patch("markdown_diagrams.validators.check_dependency")
    @patch("markdown_diagrams.validators.subprocess.run")
    def test_subprocess_exception_returns_invalid(self, mock_run, mock_dep):
        mock_dep.return_value = MagicMock(available=True)
        mock_run.side_effect = OSError("mmdc not found")
        valid, errors = validate_diagram("graph TD\n    A --> B")
        assert valid is False
        assert errors


# ---------------------------------------------------------------------------
# validate_and_fix_diagrams
# ---------------------------------------------------------------------------


class TestValidateAndFixDiagrams:
    """Tests for the orchestration function."""

    @patch("markdown_diagrams.validators.validate_diagram", return_value=(True, []))
    def test_returns_one_result_per_diagram(self, mock_validate):
        results = validate_and_fix_diagrams(DATA_DIR / "multiple_diagrams.md")
        assert len(results) == 3

    @patch("markdown_diagrams.validators.validate_diagram", return_value=(True, []))
    def test_result_indices_are_sequential(self, mock_validate):
        results = validate_and_fix_diagrams(DATA_DIR / "multiple_diagrams.md")
        assert [r.index for r in results] == [1, 2, 3]

    @patch("markdown_diagrams.validators.validate_diagram", return_value=(True, []))
    def test_headings_are_captured(self, mock_validate):
        results = validate_and_fix_diagrams(DATA_DIR / "multiple_diagrams.md")
        headings = [r.heading for r in results]
        assert "1.1 System Components" in headings
        assert "1.2 User Authentication Flow" in headings

    @patch("markdown_diagrams.validators.validate_diagram", return_value=(True, []))
    def test_no_diagrams_returns_empty_list(self, mock_validate):
        results = validate_and_fix_diagrams(DATA_DIR / "no_diagrams.md")
        assert results == []

    @patch("markdown_diagrams.validators.validate_diagram", return_value=(True, []))
    def test_nonexistent_file_returns_empty_list(self, mock_validate):
        results = validate_and_fix_diagrams(Path("/tmp/nonexistent_12345.md"))
        assert results == []

    @patch(
        "markdown_diagrams.validators.validate_diagram",
        return_value=(False, ["Error: Parse error on line 2"]),
    )
    def test_invalid_diagram_recorded(self, mock_validate):
        results = validate_and_fix_diagrams(DATA_DIR / "simple_flowchart.md")
        assert len(results) == 1
        assert results[0].valid is False
        assert results[0].errors

    @patch("markdown_diagrams.validators.validate_diagram", return_value=(True, []))
    def test_fixable_diagram_has_fixed_content(self, mock_validate):
        results = validate_and_fix_diagrams(DATA_DIR / "fixable_diagrams.md")
        # First diagram has trailing whitespace + parens — should be fixable
        assert results[0].fixed_content is not None

    @patch("markdown_diagrams.validators.validate_diagram", return_value=(True, []))
    def test_clean_diagram_fixed_content_is_structurally_unchanged(self, mock_validate):
        """A structurally clean diagram may only differ in trailing whitespace.

        The regex extractor preserves a trailing newline before the closing
        fence, which fix_diagram normalises away.  The important thing is that
        no structural changes (e.g. label quoting) are applied.
        """
        results = validate_and_fix_diagrams(DATA_DIR / "simple_flowchart.md")
        r = results[0]
        # If fixed_content is set, the only difference should be stripped whitespace
        if r.fixed_content is not None:
            assert r.fixed_content.strip() == r.content.strip()
        # No label quoting should have been introduced
        content_to_check = r.fixed_content if r.fixed_content is not None else r.content
        assert '"' not in content_to_check

    @patch("markdown_diagrams.validators.validate_diagram", return_value=(True, []))
    def test_apply_fixes_writes_back_to_file(self, mock_validate, tmp_path):
        src = DATA_DIR / "fixable_diagrams.md"
        dest = tmp_path / "fixable_diagrams.md"
        shutil.copy(src, dest)

        original = dest.read_text(encoding="utf-8")
        results = validate_and_fix_diagrams(dest, apply_fixes=True)

        patched = dest.read_text(encoding="utf-8")
        # At least the first diagram should have been fixed
        assert any(r.fixed_content is not None for r in results)
        assert patched != original

    @patch("markdown_diagrams.validators.validate_diagram", return_value=(True, []))
    def test_apply_fixes_false_does_not_modify_file(self, mock_validate, tmp_path):
        src = DATA_DIR / "fixable_diagrams.md"
        dest = tmp_path / "fixable_diagrams.md"
        shutil.copy(src, dest)

        original = dest.read_text(encoding="utf-8")
        validate_and_fix_diagrams(dest, apply_fixes=False)
        assert dest.read_text(encoding="utf-8") == original

    @patch("markdown_diagrams.validators.validate_diagram", return_value=(True, []))
    def test_fixed_content_has_no_trailing_whitespace(self, mock_validate):
        results = validate_and_fix_diagrams(DATA_DIR / "fixable_diagrams.md")
        fixed = results[0].fixed_content
        assert fixed is not None
        for line in fixed.splitlines():
            assert line == line.rstrip()


# ---------------------------------------------------------------------------
# _write_fixes
# ---------------------------------------------------------------------------


class TestWriteFixes:
    """Tests for the low-level file write helper."""

    def test_single_fix_applied(self, tmp_path):
        md = tmp_path / "test.md"
        md.write_text(
            "# H\n\n```mermaid\ngraph TD\n    A --> B\n```\n", encoding="utf-8"
        )
        content = md.read_text(encoding="utf-8")

        results = [
            ValidationResult(
                index=1,
                heading="H",
                content="graph TD\n    A --> B",
                valid=True,
                fixed_content="graph TD\n    A --> B\n    B --> C",
                start=content.index("```mermaid"),
                end=content.index("```mermaid")
                + len("```mermaid\ngraph TD\n    A --> B\n```"),
            )
        ]
        _write_fixes(md, content, results)
        written = md.read_text(encoding="utf-8")
        assert "B --> C" in written

    def test_no_fixes_leaves_file_unchanged(self, tmp_path):
        md = tmp_path / "test.md"
        original = "# H\n\n```mermaid\ngraph TD\n    A --> B\n```\n"
        md.write_text(original, encoding="utf-8")

        results = [
            ValidationResult(
                index=1,
                heading="H",
                content="graph TD\n    A --> B",
                valid=True,
                fixed_content=None,
                start=0,
                end=0,
            )
        ]
        _write_fixes(md, original, results)
        assert md.read_text(encoding="utf-8") == original

    def test_multiple_fixes_preserve_surrounding_content(self, tmp_path):
        md = tmp_path / "multi.md"
        raw = (
            "# Doc\n\n"
            "```mermaid\ngraph TD\n    A --> B   \n```\n\n"
            "Some text.\n\n"
            "```mermaid\ngraph LR\n    X --> Y   \n```\n"
        )
        md.write_text(raw, encoding="utf-8")

        # Use _write_fixes directly with hand-crafted results
        content = md.read_text(encoding="utf-8")
        start1 = content.index("```mermaid")
        end1 = content.index("```\n\nSome") + 3
        start2 = content.rindex("```mermaid")

        fixes = [
            ValidationResult(
                index=1,
                heading=None,
                content="graph TD\n    A --> B",
                valid=True,
                fixed_content="graph TD\n    A --> B",
                start=start1,
                end=end1,
            ),
            ValidationResult(
                index=2,
                heading=None,
                content="graph LR\n    X --> Y",
                valid=True,
                fixed_content="graph LR\n    X --> Y",
                start=start2,
                end=len(content),
            ),
        ]
        _write_fixes(md, content, fixes)
        written = md.read_text(encoding="utf-8")
        assert "Some text." in written


# ---------------------------------------------------------------------------
# validate CLI command
# ---------------------------------------------------------------------------


class TestValidateCLICommand:
    """Tests for the 'validate' subcommand."""

    @pytest.fixture
    def runner(self):
        return CliRunner()

    def test_help(self, runner):
        result = runner.invoke(cli, ["validate", "--help"])
        assert result.exit_code == 0
        assert "--fix" in result.output
        assert "--dry-run" in result.output

    @patch("markdown_diagrams.main._check_external_tools")
    @patch(
        "markdown_diagrams.main.validate_and_fix_diagrams",
        return_value=[
            ValidationResult(
                index=1,
                heading="Overview",
                content="graph TD\n    A --> B",
                valid=True,
            )
        ],
    )
    def test_all_valid_exits_zero(self, mock_vaf, mock_check, runner):
        result = runner.invoke(cli, ["validate", str(DATA_DIR / "simple_flowchart.md")])
        assert result.exit_code == 0
        assert "OK" in result.output

    @patch("markdown_diagrams.main._check_external_tools")
    @patch(
        "markdown_diagrams.main.validate_and_fix_diagrams",
        return_value=[
            ValidationResult(
                index=1,
                heading="Bad",
                content="graph TD\n    ???",
                valid=False,
                errors=["Error: Parse error on line 2"],
            )
        ],
    )
    def test_invalid_diagram_exits_one(self, mock_vaf, mock_check, runner):
        result = runner.invoke(cli, ["validate", str(DATA_DIR / "simple_flowchart.md")])
        assert result.exit_code == 1
        assert "FAIL" in result.output

    @patch("markdown_diagrams.main._check_external_tools")
    @patch(
        "markdown_diagrams.main.validate_and_fix_diagrams",
        return_value=[
            ValidationResult(
                index=1,
                heading="Flow",
                content="flowchart TD\n    A[foo(x)] --> B[OK]",
                valid=False,
                errors=["Error: Parse error"],
                fixed_content='flowchart TD\n    A["foo(x)"] --> B[OK]',
            )
        ],
    )
    def test_fix_flag_applies_fixes(self, mock_vaf, mock_check, runner):
        result = runner.invoke(
            cli,
            ["validate", "--fix", str(DATA_DIR / "simple_flowchart.md")],
        )
        assert result.exit_code == 0
        assert "Applied fixes" in result.output
        mock_vaf.assert_called_once_with(
            Path(str(DATA_DIR / "simple_flowchart.md")), apply_fixes=True
        )

    @patch("markdown_diagrams.main._check_external_tools")
    @patch(
        "markdown_diagrams.main.validate_and_fix_diagrams",
        return_value=[
            ValidationResult(
                index=1,
                heading="Flow",
                content="flowchart TD\n    A[foo(x)] --> B[OK]",
                valid=True,
                fixed_content='flowchart TD\n    A["foo(x)"] --> B[OK]',
            )
        ],
    )
    def test_dry_run_shows_message_without_writing(self, mock_vaf, mock_check, runner):
        result = runner.invoke(
            cli,
            ["validate", "--dry-run", str(DATA_DIR / "simple_flowchart.md")],
        )
        assert result.exit_code == 0
        assert "[dry-run]" in result.output
        assert "could be auto-fixed" in result.output
        # apply_fixes must be False for dry-run
        mock_vaf.assert_called_once_with(
            Path(str(DATA_DIR / "simple_flowchart.md")), apply_fixes=False
        )

    @patch("markdown_diagrams.main._check_external_tools")
    def test_fix_and_dry_run_mutually_exclusive(self, mock_check, runner):
        result = runner.invoke(
            cli,
            [
                "validate",
                "--fix",
                "--dry-run",
                str(DATA_DIR / "simple_flowchart.md"),
            ],
        )
        assert result.exit_code != 0

    @patch("markdown_diagrams.main._check_external_tools")
    @patch("markdown_diagrams.main.validate_and_fix_diagrams", return_value=[])
    def test_no_diagrams_found(self, mock_vaf, mock_check, runner):
        result = runner.invoke(cli, ["validate", str(DATA_DIR / "no_diagrams.md")])
        assert result.exit_code == 0
        assert "No Mermaid diagrams found" in result.output
