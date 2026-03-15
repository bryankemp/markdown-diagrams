#!/usr/bin/env python3
"""
Extractor functions for parsing content from Markdown files.
"""

import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Set up logging
logger = logging.getLogger(__name__)

# Supported diagram types with their regex patterns.
# Be careful with pattern matching to avoid issues
# with nested code blocks.
DIAGRAM_PATTERNS = {
    "mermaid": r"```(?:mermaid)(.*?```)",
    "flowchart": r"```(?:flowchart)(.*?```)",
    "sequence": r"```(?:sequence)(.*?```)",
    "graph": r"```(?:graph)(.*?```)",
    "gantt": r"```(?:gantt)(.*?```)",
    "pie": r"```(?:pie)(.*?```)",
    "toc": r"```(?:toc)(.*?```)",
    "mindmap": r"```(?:mindmap)(.*?```)",
    "quadrantDiagram": r"```(?:quadrantDiagram)(.*?```)",
    "er": r"```(?:er)(.*?```)",
    "class": r"```(?:class)(.*?```)",
    "state": r"```(?:state)(.*?```)",
    "journey": r"```(?:journey)(.*?```)",
    "active": r"```(?:active)(.*?```)",
    "component": r"```(?:component)(.*?```)",
    "gitGraph": r"```(?:gitGraph)(.*?```)",
    "userJourney": r"```(?:userJourney)(.*?```)",
    "requirement": r"```(?:requirement)(.*?```)",
    "c4": r"```(?:c4)(.*?```)",
    "entityRelationship": r"```(?:entityRelationship)(.*?```)",
}

# Mapping from code fence type to the Mermaid diagram type declaration
# that must be prepended to the extracted content.
# None means the content already includes the diagram type (e.g. ```mermaid blocks).
DIAGRAM_TYPE_PREFIX = {
    "mermaid": None,
    "flowchart": "flowchart",
    "sequence": "sequenceDiagram",
    "graph": "graph",
    "gantt": "gantt",
    "pie": "pie",
    "toc": None,
    "mindmap": "mindmap",
    "quadrantDiagram": "quadrantChart",
    "er": "erDiagram",
    "class": "classDiagram",
    "state": "stateDiagram-v2",
    "journey": "journey",
    "active": None,
    "component": None,
    "gitGraph": "gitGraph",
    "userJourney": "journey",
    "requirement": "requirementDiagram",
    "c4": "C4Context",
    "entityRelationship": "erDiagram",
}


def _find_preceding_heading(content: str, position: int) -> Optional[str]:
    """Find the nearest markdown heading before the given position.

    Args:
        content: The full markdown file content.
        position: The character offset of the diagram code fence.

    Returns:
        The heading text (without ``#`` markers), or None if no heading is found.
    """
    heading_pattern = r"^(#{1,6})\s+(.+)$"
    last_heading = None
    for match in re.finditer(heading_pattern, content[:position], re.MULTILINE):
        last_heading = match.group(2).strip()
    return last_heading


def _find_preceding_label(
    content: str, position: int, max_lines_back: int = 5
) -> Optional[str]:
    """Find a descriptive bold-text label immediately before a diagram fence.

    Many Markdown documents place a descriptive title in bold text
    (``**Title**``) on the line(s) just above a code fence, while the
    nearest ``#``-heading is a generic section name like "Diagrams".
    This function returns that bold label when present so it can be
    used for a more descriptive filename.

    Args:
        content: The full markdown file content.
        position: The character offset of the diagram code fence.
        max_lines_back: How many lines before the fence to search.

    Returns:
        The bold label text (without ``**`` markers), or None.
    """
    # Grab the text just before the code fence and split into lines.
    preceding = content[:position].rstrip()
    lines = preceding.split("\n")
    search_lines = lines[-max_lines_back:] if len(lines) >= max_lines_back else lines

    # Walk backwards to find the closest bold-text label.
    bold_pattern = re.compile(r"^\s*\*\*(.+?)\*\*\s*$")
    for line in reversed(search_lines):
        stripped = line.strip()
        if not stripped:
            continue
        m = bold_pattern.match(stripped)
        if m:
            return m.group(1).strip()
        # Stop searching once we hit non-empty, non-bold content.
        break
    return None


def heading_to_filename(heading: str) -> str:
    """Convert a markdown heading to a filesystem-safe filename stem.

    Args:
        heading: Raw heading text (e.g. ``3.1 System Architecture``).

    Returns:
        A lowercase, underscore-separated filename stem
        (e.g. ``system_architecture``).
    """
    # Strip leading section numbers like "3.1" or "6.2"
    name = re.sub(r"^[\d.]+\s*", "", heading)
    name = name.lower()
    # Replace non-alphanumeric runs with a single underscore
    name = re.sub(r"[^a-z0-9]+", "_", name)
    name = name.strip("_")
    # Truncate overly long names
    if len(name) > 60:
        name = name[:60].rstrip("_")
    return name or "diagram"


def extract_diagrams(
    markdown_file: Path, diagram_types: List[str] = None
) -> Dict[str, List[Dict[str, Any]]]:
    """Extract diagrams from a Markdown file.

    Args:
        markdown_file: Path to the Markdown file.
        diagram_types: List of diagram types to extract.
            If None, extract all supported types.

    Returns:
        Dictionary mapping diagram type to a list of dicts, each with:
            - ``content``: The diagram source text.
            - ``heading``: The best available label for the diagram: a
              bold-text title immediately above the fence if present,
              otherwise the nearest preceding markdown heading, or None.
    """
    # Initialize result dictionary
    result: Dict[str, List[Dict[str, Any]]] = {
        dtype: [] for dtype in DIAGRAM_PATTERNS.keys()
    }

    # If no specific types requested, extract all
    if diagram_types is None:
        diagram_types = list(DIAGRAM_PATTERNS.keys())

    # Verify that requested diagram types are supported
    unsupported_types = [
        dtype for dtype in diagram_types if dtype not in DIAGRAM_PATTERNS
    ]
    if unsupported_types:
        logger.warning(f"Unsupported diagram types requested: {unsupported_types}")
        diagram_types = [dtype for dtype in diagram_types if dtype in DIAGRAM_PATTERNS]

    try:
        # Read the file content with error handling
        try:
            content = markdown_file.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            logger.error(f"Failed to read file {markdown_file} - encoding error")
            return result
        except Exception as e:
            logger.error(f"Failed to read file {markdown_file}: {str(e)}")
            return result

        # Extract each requested diagram type
        for diagram_type in diagram_types:
            pattern = DIAGRAM_PATTERNS[diagram_type]
            try:
                prefix = DIAGRAM_TYPE_PREFIX.get(diagram_type)
                diagrams: List[Dict[str, Any]] = []
                for match in re.finditer(pattern, content, re.DOTALL | re.IGNORECASE):
                    diagram_content = match.group(1).strip().rstrip("`")
                    if diagram_content:
                        if prefix:
                            diagram_content = f"{prefix}\n{diagram_content}"
                        label = _find_preceding_label(content, match.start())
                        heading = label or _find_preceding_heading(
                            content, match.start()
                        )
                        diagrams.append(
                            {"content": diagram_content, "heading": heading}
                        )
                result[diagram_type] = diagrams
            except Exception as e:
                logger.error(
                    f"Error extracting {diagram_type} diagrams "
                    f"from {markdown_file}: {e}"
                )
                result[diagram_type] = []

    except Exception as e:
        logger.error(f"Unexpected error processing {markdown_file}: {str(e)}")

    return result


def extract_mermaid_diagrams(markdown_file: Path) -> List[str]:
    """Extract Mermaid diagrams from a Markdown file (legacy function).

    Args:
        markdown_file: Path to the Markdown file.

    Returns:
        List of Mermaid diagram content strings.
    """
    try:
        diagrams = extract_diagrams(markdown_file, ["mermaid"])
        return [d["content"] for d in diagrams["mermaid"]]
    except Exception as e:
        logger.error(f"Error extracting Mermaid diagrams: {str(e)}")
        return []


def extract_diagrams_with_position(
    markdown_file: Path, diagram_type: str = "mermaid"
) -> List[Tuple[str, int, int]]:
    """
    Extract diagrams along with their position in the file.

    Args:
        markdown_file: Path to the Markdown file
        diagram_type: Type of diagram to extract positions for

    Returns:
        List of tuples containing (diagram_content, start_position, end_position)
    """
    try:
        content = markdown_file.read_text(encoding="utf-8")
        pattern = DIAGRAM_PATTERNS[diagram_type]

        # Find all matches with position
        diagrams = []
        for match in re.finditer(pattern, content, re.DOTALL | re.IGNORECASE):
            # Extract just the diagram content (without the ``` markers or
            # the trailing newline that precedes the closing fence).
            diagram_content = match.group(1).strip().rstrip("`").strip()
            diagrams.append((diagram_content, match.start(), match.end()))

        return diagrams
    except Exception as e:
        logger.error(
            f"Error extracting {diagram_type} diagrams with position: {str(e)}"
        )
        return []
