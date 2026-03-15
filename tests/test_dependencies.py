"""Tests for the markdown_diagrams.dependencies module."""

from unittest.mock import MagicMock, patch

import pytest

from markdown_diagrams.dependencies import (
    MERMAID_CLI,
    Dependency,
    DependencyStatus,
    check_all,
    check_dependency,
    format_missing_message,
    require_all,
)

FAKE_DEP = Dependency(
    name="Fake Tool",
    command="faketool",
    version_flag="--version",
    why="Needed for testing.",
    install_instructions=["pip install faketool", "brew install faketool"],
    url="https://example.com/faketool",
)


# ---------------------------------------------------------------------------
# check_dependency
# ---------------------------------------------------------------------------


class TestCheckDependency:
    @patch("markdown_diagrams.dependencies.shutil.which", return_value="/usr/bin/mmdc")
    @patch("markdown_diagrams.dependencies.subprocess.run")
    def test_available_with_version(self, mock_run, mock_which):
        mock_run.return_value = MagicMock(returncode=0, stdout="10.6.1", stderr="")
        status = check_dependency(MERMAID_CLI)
        assert status.available is True
        assert status.version == "10.6.1"

    @patch("markdown_diagrams.dependencies.shutil.which", return_value=None)
    def test_not_available(self, mock_which):
        status = check_dependency(MERMAID_CLI)
        assert status.available is False
        assert status.version is None

    @patch("markdown_diagrams.dependencies.shutil.which", return_value="/usr/bin/mmdc")
    @patch("markdown_diagrams.dependencies.subprocess.run", side_effect=OSError)
    def test_available_but_version_fails(self, mock_run, mock_which):
        """Binary exists but --version crashes — still marked available."""
        status = check_dependency(MERMAID_CLI)
        assert status.available is True
        assert status.version is None


# ---------------------------------------------------------------------------
# check_all
# ---------------------------------------------------------------------------


class TestCheckAll:
    @patch("markdown_diagrams.dependencies.shutil.which", return_value="/usr/bin/mmdc")
    @patch("markdown_diagrams.dependencies.subprocess.run")
    def test_returns_list(self, mock_run, mock_which):
        mock_run.return_value = MagicMock(returncode=0, stdout="1.0", stderr="")
        statuses = check_all()
        assert isinstance(statuses, list)
        assert len(statuses) >= 1


# ---------------------------------------------------------------------------
# format_missing_message
# ---------------------------------------------------------------------------


class TestFormatMissingMessage:
    def test_contains_name_and_instructions(self):
        status = DependencyStatus(dependency=FAKE_DEP, available=False)
        msg = format_missing_message(status)
        assert "Fake Tool" in msg
        assert "pip install faketool" in msg
        assert "brew install faketool" in msg
        assert "https://example.com/faketool" in msg

    def test_contains_why(self):
        status = DependencyStatus(dependency=FAKE_DEP, available=False)
        msg = format_missing_message(status)
        assert "Needed for testing." in msg

    @patch("markdown_diagrams.dependencies.platform.system", return_value="Darwin")
    def test_macos_hint(self, mock_sys):
        status = DependencyStatus(dependency=MERMAID_CLI, available=False)
        msg = format_missing_message(status)
        assert "brew install node" in msg

    @patch("markdown_diagrams.dependencies.platform.system", return_value="Linux")
    def test_linux_hint(self, mock_sys):
        status = DependencyStatus(dependency=MERMAID_CLI, available=False)
        msg = format_missing_message(status)
        assert "nvm" in msg

    @patch("markdown_diagrams.dependencies.platform.system", return_value="Windows")
    def test_windows_hint(self, mock_sys):
        status = DependencyStatus(dependency=MERMAID_CLI, available=False)
        msg = format_missing_message(status)
        assert "nodejs.org" in msg


# ---------------------------------------------------------------------------
# require_all
# ---------------------------------------------------------------------------


class TestRequireAll:
    @patch("markdown_diagrams.dependencies.shutil.which", return_value="/usr/bin/mmdc")
    @patch("markdown_diagrams.dependencies.subprocess.run")
    def test_all_present(self, mock_run, mock_which):
        mock_run.return_value = MagicMock(returncode=0, stdout="1.0", stderr="")
        statuses = require_all(strict=True)
        assert all(s.available for s in statuses)

    @patch("markdown_diagrams.dependencies.shutil.which", return_value=None)
    def test_strict_exits(self, mock_which):
        with pytest.raises(SystemExit):
            require_all(strict=True)

    @patch("markdown_diagrams.dependencies.shutil.which", return_value=None)
    def test_non_strict_does_not_exit(self, mock_which):
        statuses = require_all(strict=False)
        assert any(not s.available for s in statuses)
