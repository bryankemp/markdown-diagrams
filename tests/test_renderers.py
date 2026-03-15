"""Tests for the markdown_diagrams.renderers module."""

from unittest.mock import MagicMock, patch

from markdown_diagrams.renderers import (
    _sanitize_mermaid_content,
    check_mermaid_cli,
    get_mermaid_version,
    render_mermaid_diagram,
    render_mermaid_to_pdf,
    render_mermaid_to_png,
    render_mermaid_to_svg,
)

SAMPLE_DIAGRAM = "graph TD\n    A --> B\n"


# ---------------------------------------------------------------------------
# check_mermaid_cli
# ---------------------------------------------------------------------------


class TestCheckMermaidCli:
    @patch("markdown_diagrams.dependencies.shutil.which", return_value="/usr/bin/mmdc")
    def test_available(self, mock_which):
        assert check_mermaid_cli() is True

    @patch("markdown_diagrams.dependencies.shutil.which", return_value=None)
    def test_not_available(self, mock_which):
        assert check_mermaid_cli() is False


# ---------------------------------------------------------------------------
# render_mermaid_to_png
# ---------------------------------------------------------------------------


class TestRenderToPng:
    @patch("markdown_diagrams.renderers.check_dependency")
    @patch("markdown_diagrams.renderers.subprocess.run")
    def test_success(self, mock_run, mock_dep, tmp_path):
        mock_dep.return_value = MagicMock(available=True)
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        out = str(tmp_path / "test.png")
        assert render_mermaid_to_png(SAMPLE_DIAGRAM, out) is True

    @patch("markdown_diagrams.renderers.check_dependency")
    def test_missing_cli(self, mock_dep, tmp_path):
        mock_dep.return_value = MagicMock(available=False)
        out = str(tmp_path / "test.png")
        assert render_mermaid_to_png(SAMPLE_DIAGRAM, out) is False

    @patch("markdown_diagrams.renderers.check_dependency")
    @patch("markdown_diagrams.renderers.subprocess.run")
    def test_render_failure(self, mock_run, mock_dep, tmp_path):
        mock_dep.return_value = MagicMock(available=True)
        mock_run.return_value = MagicMock(returncode=1, stderr="parse error")
        out = str(tmp_path / "test.png")
        assert render_mermaid_to_png(SAMPLE_DIAGRAM, out) is False

    @patch("markdown_diagrams.renderers.check_dependency")
    @patch("markdown_diagrams.renderers.subprocess.run")
    def test_custom_theme(self, mock_run, mock_dep, tmp_path):
        mock_dep.return_value = MagicMock(available=True)
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        out = str(tmp_path / "test.png")
        render_mermaid_to_png(SAMPLE_DIAGRAM, out, theme="dark")
        cmd = mock_run.call_args[0][0]
        assert "-t" in cmd
        assert "dark" in cmd


# ---------------------------------------------------------------------------
# render_mermaid_to_svg
# ---------------------------------------------------------------------------


class TestRenderToSvg:
    @patch("markdown_diagrams.renderers.check_dependency")
    @patch("markdown_diagrams.renderers.subprocess.run")
    def test_success(self, mock_run, mock_dep, tmp_path):
        mock_dep.return_value = MagicMock(available=True)
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        out = str(tmp_path / "test.svg")
        assert render_mermaid_to_svg(SAMPLE_DIAGRAM, out) is True

    @patch("markdown_diagrams.renderers.check_dependency")
    def test_missing_cli(self, mock_dep, tmp_path):
        mock_dep.return_value = MagicMock(available=False)
        out = str(tmp_path / "test.svg")
        assert render_mermaid_to_svg(SAMPLE_DIAGRAM, out) is False


# ---------------------------------------------------------------------------
# render_mermaid_to_pdf
# ---------------------------------------------------------------------------


class TestRenderToPdf:
    @patch("markdown_diagrams.renderers.check_dependency")
    @patch("markdown_diagrams.renderers.subprocess.run")
    def test_success(self, mock_run, mock_dep, tmp_path):
        mock_dep.return_value = MagicMock(available=True)
        mock_run.return_value = MagicMock(returncode=0, stderr="")
        out = str(tmp_path / "test.pdf")
        assert render_mermaid_to_pdf(SAMPLE_DIAGRAM, out) is True

    @patch("markdown_diagrams.renderers.check_dependency")
    def test_missing_cli(self, mock_dep, tmp_path):
        mock_dep.return_value = MagicMock(available=False)
        out = str(tmp_path / "test.pdf")
        assert render_mermaid_to_pdf(SAMPLE_DIAGRAM, out) is False


# ---------------------------------------------------------------------------
# render_mermaid_diagram (dispatcher)
# ---------------------------------------------------------------------------


class TestRenderMermaidDiagram:
    @patch("markdown_diagrams.renderers.render_mermaid_to_png", return_value=True)
    def test_png_dispatch(self, mock_png, tmp_path):
        result = render_mermaid_diagram(SAMPLE_DIAGRAM, str(tmp_path), "png")
        assert result is not None
        assert result.endswith(".png")
        mock_png.assert_called_once()

    @patch("markdown_diagrams.renderers.render_mermaid_to_svg", return_value=True)
    def test_svg_dispatch(self, mock_svg, tmp_path):
        result = render_mermaid_diagram(SAMPLE_DIAGRAM, str(tmp_path), "svg")
        assert result is not None
        assert result.endswith(".svg")

    @patch("markdown_diagrams.renderers.render_mermaid_to_pdf", return_value=True)
    def test_pdf_dispatch(self, mock_pdf, tmp_path):
        result = render_mermaid_diagram(SAMPLE_DIAGRAM, str(tmp_path), "pdf")
        assert result is not None
        assert result.endswith(".pdf")

    def test_unsupported_format(self, tmp_path):
        result = render_mermaid_diagram(SAMPLE_DIAGRAM, str(tmp_path), "bmp")
        assert result is None

    @patch("markdown_diagrams.renderers.render_mermaid_to_png", return_value=True)
    def test_custom_name(self, mock_png, tmp_path):
        result = render_mermaid_diagram(
            SAMPLE_DIAGRAM, str(tmp_path), "png", name="my_chart"
        )
        assert result is not None
        assert "my_chart.png" in result

    @patch("markdown_diagrams.renderers.render_mermaid_to_png", return_value=True)
    def test_hash_fallback_name(self, mock_png, tmp_path):
        result = render_mermaid_diagram(SAMPLE_DIAGRAM, str(tmp_path), "png")
        assert result is not None
        assert "diagram_" in result


# ---------------------------------------------------------------------------
# get_mermaid_version
# ---------------------------------------------------------------------------


class TestGetMermaidVersion:
    @patch("markdown_diagrams.renderers.subprocess.run")
    def test_returns_version(self, mock_run):
        mock_run.return_value = MagicMock(returncode=0, stdout="10.6.1\n")
        assert get_mermaid_version() == "10.6.1"

    @patch("markdown_diagrams.renderers.subprocess.run")
    def test_not_installed(self, mock_run):
        mock_run.side_effect = FileNotFoundError
        assert get_mermaid_version() is None


# ---------------------------------------------------------------------------
# _sanitize_mermaid_content
# ---------------------------------------------------------------------------


class TestSanitizeMermaidContent:
    def test_quotes_parens_in_flowchart_labels(self):
        content = "flowchart TD\n    A[call foo(x)] --> B[OK]"
        result = _sanitize_mermaid_content(content)
        assert '["call foo(x)"]' in result
        assert "[OK]" in result

    def test_quotes_parens_in_graph_labels(self):
        content = "graph TD\n    A[Device Detected (AddDevice / probe)]"
        result = _sanitize_mermaid_content(content)
        assert '["Device Detected (AddDevice / probe)"]' in result

    def test_no_change_for_sequence_diagram(self):
        content = "sequenceDiagram\n    A->>B: call foo(x)"
        assert _sanitize_mermaid_content(content) == content

    def test_no_change_when_no_parens(self):
        content = "flowchart TD\n    A[Start] --> B[End]"
        assert _sanitize_mermaid_content(content) == content

    def test_already_quoted_labels_unchanged(self):
        content = 'flowchart TD\n    A["already quoted (parens)"] --> B[OK]'
        assert _sanitize_mermaid_content(content) == content

    def test_compound_shape_cylindrical_unchanged(self):
        content = "flowchart TD\n    A[(Database)] --> B[OK]"
        result = _sanitize_mermaid_content(content)
        assert "[(Database)]" in result

    def test_compound_shape_parallelogram_unchanged(self):
        content = "flowchart TD\n    A[/Parallelogram/] --> B[OK]"
        result = _sanitize_mermaid_content(content)
        assert "[/Parallelogram/]" in result

    def test_empty_content(self):
        assert _sanitize_mermaid_content("") == ""

    def test_multiple_labels_with_parens(self):
        content = (
            "flowchart TD\n"
            "    A[IsEnabled(feat)] --> B{Check?}\n"
            "    B -->|Yes| C[Grant(token)]\n"
        )
        result = _sanitize_mermaid_content(content)
        assert '["IsEnabled(feat)"]' in result
        assert '["Grant(token)"]' in result

    def test_quotes_parens_in_diamond_labels(self):
        content = "flowchart TD\n    B{Check Central Pool (Lease Available)?}"
        result = _sanitize_mermaid_content(content)
        assert '{"Check Central Pool (Lease Available)?"}' in result

    def test_diamond_without_parens_unchanged(self):
        content = "flowchart TD\n    B{Is Valid?}"
        assert _sanitize_mermaid_content(content) == content

    def test_hexagon_shape_unchanged(self):
        content = "flowchart TD\n    A{{Hexagon}}"
        assert _sanitize_mermaid_content(content) == content

    def test_quotes_parens_in_edge_labels(self):
        content = (
            "flowchart TD\n" "    H -->|Yes (feature requested)| I[Send Request]\n"
        )
        result = _sanitize_mermaid_content(content)
        assert '|"Yes (feature requested)"|' in result

    def test_edge_label_without_parens_unchanged(self):
        content = "flowchart TD\n    A -->|Yes| B[End]"
        assert _sanitize_mermaid_content(content) == content

    def test_real_world_entitlement_label(self):
        content = (
            "flowchart TD\n"
            "    D[Read Signed License Token (Cert + Nonce)]\n"
            "    G[Driver Calls EntitlementService::InjectHardwareLicense"
            "(token, deviceID)]\n"
        )
        result = _sanitize_mermaid_content(content)
        assert '["Read Signed License Token (Cert + Nonce)"]' in result
        assert '"Driver Calls EntitlementService::InjectHardwareLicense' in result
