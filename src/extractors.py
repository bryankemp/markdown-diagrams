#!/usr/bin/env python3
"""
Extractor functions for parsing content from Markdown files.
"""

import re
from pathlib import Path
from typing import List, Tuple


def extract_mermaid_diagrams(markdown_file: Path) -> List[str]:
    """
    Extract Mermaid diagrams from a Markdown file.

    Args:
        markdown_file: Path to the Markdown file

    Returns:
        List of Mermaid diagram strings
    """
    # Read the file content
    content = markdown_file.read_text(encoding="utf-8")

    # Pattern to match Mermaid code blocks
    pattern = r"```(?:mermaid)(.*?)```"

    # Find all matches
    matches = re.findall(pattern, content, re.DOTALL | re.IGNORECASE)

    # Strip whitespace from each diagram
    diagrams = [diagram.strip() for diagram in matches if diagram.strip()]

    return diagrams


def extract_diagrams_with_position(markdown_file: Path) -> List[Tuple[str, int, int]]:
    """
    Extract Mermaid diagrams along with their position in the file.

    Args:
        markdown_file: Path to the Markdown file

    Returns:
        List of tuples containing (diagram_content, start_position, end_position)
    """
    content = markdown_file.read_text(encoding="utf-8")

    # Pattern to match Mermaid code blocks with position
    pattern = r"```(?:mermaid)(.*?)```"

    # Find all matches with position
    diagrams = []
    for match in re.finditer(pattern, content, re.DOTALL | re.IGNORECASE):
        diagrams.append((match.group(1).strip(), match.start(), match.end()))

    return diagrams
