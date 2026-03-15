"""Tests for the markdown_diagrams.extractors module."""

from pathlib import Path

from markdown_diagrams.extractors import (
    DIAGRAM_PATTERNS,
    _find_preceding_heading,
    extract_diagrams,
    extract_diagrams_with_position,
    extract_mermaid_diagrams,
    heading_to_filename,
)

DATA_DIR = Path(__file__).parent / "data"


# ---------------------------------------------------------------------------
# extract_diagrams
# ---------------------------------------------------------------------------


class TestExtractDiagrams:
    """Tests for the main extract_diagrams function."""

    def test_single_mermaid_diagram(self):
        """Extract a single mermaid diagram from a simple file."""
        result = extract_diagrams(DATA_DIR / "simple_flowchart.md")
        assert len(result["mermaid"]) == 1
        assert "graph TD" in result["mermaid"][0]["content"]

    def test_heading_is_captured(self):
        """The nearest preceding heading is attached to each diagram."""
        result = extract_diagrams(DATA_DIR / "simple_flowchart.md")
        assert result["mermaid"][0]["heading"] == "Process Overview"

    def test_multiple_diagrams(self):
        """Extract multiple diagrams from a single file."""
        result = extract_diagrams(DATA_DIR / "multiple_diagrams.md")
        assert len(result["mermaid"]) == 3

    def test_multiple_diagram_headings(self):
        """Each diagram gets its own preceding heading."""
        result = extract_diagrams(DATA_DIR / "multiple_diagrams.md")
        headings = [d["heading"] for d in result["mermaid"]]
        assert "1.1 System Components" in headings
        assert "1.2 User Authentication Flow" in headings
        assert "1.3 Deployment Pipeline" in headings

    def test_no_diagrams(self):
        """A file with no diagrams returns empty lists."""
        result = extract_diagrams(DATA_DIR / "no_diagrams.md")
        for diagrams in result.values():
            assert diagrams == []

    def test_empty_file(self):
        """An empty file returns empty lists without errors."""
        result = extract_diagrams(DATA_DIR / "empty.md")
        assert isinstance(result, dict)
        for diagrams in result.values():
            assert diagrams == []

    def test_mixed_diagram_types(self):
        """Mermaid and ER diagram types are both extracted."""
        result = extract_diagrams(DATA_DIR / "mixed_types.md")
        assert len(result["mermaid"]) == 2  # classDiagram + stateDiagram
        assert len(result["er"]) == 1

    def test_filter_by_type(self):
        """Only the requested diagram types are populated."""
        result = extract_diagrams(DATA_DIR / "multiple_diagrams.md", ["mermaid"])
        assert len(result["mermaid"]) == 3
        assert result["flowchart"] == []

    def test_unsupported_type_is_ignored(self):
        """Unsupported diagram types are silently skipped."""
        result = extract_diagrams(
            DATA_DIR / "simple_flowchart.md", ["mermaid", "nonexistent"]
        )
        assert len(result["mermaid"]) == 1

    def test_nonexistent_file_returns_empty(self):
        """A missing file logs an error and returns the empty-dict structure."""
        result = extract_diagrams(Path("/tmp/does_not_exist_12345.md"))
        assert isinstance(result, dict)
        for diagrams in result.values():
            assert diagrams == []

    def test_er_diagram_gets_prefix(self):
        """ER diagrams extracted from ```er fences get the erDiagram prefix."""
        result = extract_diagrams(DATA_DIR / "mixed_types.md", ["er"])
        assert len(result["er"]) == 1
        assert result["er"][0]["content"].startswith("erDiagram")

    def test_result_keys_match_all_patterns(self):
        """The result dict always contains a key for every known pattern."""
        result = extract_diagrams(DATA_DIR / "empty.md")
        assert set(result.keys()) == set(DIAGRAM_PATTERNS.keys())


# ---------------------------------------------------------------------------
# extract_mermaid_diagrams (legacy)
# ---------------------------------------------------------------------------


class TestExtractMermaidDiagrams:
    """Tests for the legacy extract_mermaid_diagrams wrapper."""

    def test_returns_list_of_strings(self):
        diagrams = extract_mermaid_diagrams(DATA_DIR / "simple_flowchart.md")
        assert isinstance(diagrams, list)
        assert len(diagrams) == 1
        assert isinstance(diagrams[0], str)

    def test_nonexistent_file_returns_empty_list(self):
        diagrams = extract_mermaid_diagrams(Path("/tmp/nope_12345.md"))
        assert diagrams == []


# ---------------------------------------------------------------------------
# extract_diagrams_with_position
# ---------------------------------------------------------------------------


class TestExtractDiagramsWithPosition:
    """Tests for position-aware extraction."""

    def test_returns_tuples(self):
        result = extract_diagrams_with_position(DATA_DIR / "simple_flowchart.md")
        assert len(result) == 1
        content, start, end = result[0]
        assert isinstance(content, str)
        assert isinstance(start, int)
        assert end > start

    def test_multiple_positions(self):
        result = extract_diagrams_with_position(DATA_DIR / "multiple_diagrams.md")
        assert len(result) == 3
        positions = [start for _, start, _ in result]
        assert positions == sorted(positions)

    def test_nonexistent_file_returns_empty(self):
        result = extract_diagrams_with_position(Path("/tmp/nope_12345.md"))
        assert result == []


# ---------------------------------------------------------------------------
# heading_to_filename
# ---------------------------------------------------------------------------


class TestHeadingToFilename:
    """Tests for the heading_to_filename helper."""

    def test_basic(self):
        assert heading_to_filename("System Architecture") == "system_architecture"

    def test_strips_section_numbers(self):
        assert heading_to_filename("3.1 System Architecture") == "system_architecture"
        assert heading_to_filename("6.2.1 Details") == "details"

    def test_special_characters(self):
        assert heading_to_filename("Hello, World! (v2)") == "hello_world_v2"

    def test_empty_after_strip(self):
        assert heading_to_filename("3.1") == "diagram"

    def test_truncation(self):
        long_heading = "a" * 100
        result = heading_to_filename(long_heading)
        assert len(result) <= 60

    def test_leading_trailing_underscores_stripped(self):
        assert heading_to_filename("  --Foo--  ") == "foo"


# ---------------------------------------------------------------------------
# _find_preceding_heading
# ---------------------------------------------------------------------------


class TestFindPrecedingHeading:
    """Tests for the _find_preceding_heading helper."""

    def test_finds_nearest_heading(self):
        content = "# Top\n\nSome text\n\n## Section A\n\nMore text\n"
        assert _find_preceding_heading(content, len(content)) == "Section A"

    def test_no_heading(self):
        content = "Just some text with no headings.\n"
        assert _find_preceding_heading(content, len(content)) is None

    def test_position_before_any_heading(self):
        content = "Preamble\n# Heading\n"
        assert _find_preceding_heading(content, 5) is None

    def test_multiple_heading_levels(self):
        content = "# H1\n## H2\n### H3\ntext"
        assert _find_preceding_heading(content, len(content)) == "H3"
