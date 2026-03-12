#!/usr/bin/env python3
"""
Extractor functions for parsing content from Markdown files.
"""

import re
from pathlib import Path
from typing import List, Tuple, Dict, Any
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Supported diagram types with their regex patterns
DIAGRAM_PATTERNS = {
    "mermaid": r"```(?:mermaid)(.*?```)",
    "flowchart": r"```(?:flowchart)(.*?```)",
    "sequence": r"```(?:sequence)(.*?```)",
    "graph": r"```(?:graph)(.*?```)",
    "gantt": r"```(?:gantt)(.*?```)",
    "pie": r"```(?:pie)(.*?```)",
    "toc": r"```(?:toc)(.*?```)",
    "mindmap": r"```(?:mindmap)(.*?```)",
    " quadrantDiagram": r"```(?:quadrantDiagram)(.*?```)",
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


def extract_diagrams(
    markdown_file: Path, diagram_types: List[str] = None
) -> Dict[str, List[str]]:
    """
    Extract diagrams from a Markdown file.

    Args:
        markdown_file: Path to the Markdown file
        diagram_types: List of diagram types to extract. If None, extract all supported types.

    Returns:
        Dictionary mapping diagram type to list of diagram strings
    """
    # Initialize result dictionary
    result = {dtype: [] for dtype in DIAGRAM_PATTERNS.keys()}

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
                matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)
                # Strip the closing ``` from each match
                diagrams = [
                    match.strip().rstrip("`") for match in matches if match.strip()
                ]
                result[diagram_type] = diagrams
            except Exception as e:
                logger.error(
                    f"Error extracting {diagram_type} diagrams from {markdown_file}: {str(e)}"
                )
                result[diagram_type] = []

    except Exception as e:
        logger.error(f"Unexpected error processing {markdown_file}: {str(e)}")

    return result


def extract_mermaid_diagrams(markdown_file: Path) -> List[str]:
    """
    Extract Mermaid diagrams from a Markdown file (legacy function).

    Args:
        markdown_file: Path to the Markdown file

    Returns:
        List of Mermaid diagram strings
    """
    try:
        diagrams = extract_diagrams(markdown_file, ["mermaid"])
        return diagrams["mermaid"]
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
            # Extract just the diagram content (without the ``` markers)
            diagram_content = match.group(1).strip().rstrip("`")
            diagrams.append((diagram_content, match.start(), match.end()))

        return diagrams
    except Exception as e:
        logger.error(
            f"Error extracting {diagram_type} diagrams with position: {str(e)}"
        )
        return []
