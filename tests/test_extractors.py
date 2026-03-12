"""
Test cases for extractors module.
"""

import tempfile
import os
from pathlib import Path
from src.extractors import extract_mermaid_diagrams, extract_diagrams_with_position


def test_extract_mermaid_diagrams():
    """Test extraction of Mermaid diagrams from Markdown content."""
    # Create test Markdown content with Mermaid diagrams
    test_content = """
# Test Document

This is some text.

```mermaid
graph TD
    A[Start] --> B{Decision}
    B --> C[Process]
    C --> D[End]
```

More text here.

```mermaid
sequenceDiagram
    participant Alice
    participant Bob
    Alice->>Bob: Hello Bob, how are you?
    Bob-->>Alice: I'm good thanks!
```

Even more text.
"""

    # Create a temporary file for testing
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(test_content)
        temp_path = Path(f.name)

    try:
        # Extract diagrams
        diagrams = extract_mermaid_diagrams(temp_path)

        # Should find 2 diagrams
        assert len(diagrams) == 2

        # Check first diagram content
        assert "graph TD" in diagrams[0]
        assert "A[Start]" in diagrams[0]

        # Check second diagram content
        assert "sequenceDiagram" in diagrams[1]
        assert "participant Alice" in diagrams[1]

    finally:
        # Clean up temp file
        os.unlink(temp_path)


def test_extract_diagrams_with_position():
    """Test extraction of Mermaid diagrams with their positions."""
    test_content = """
# Test Document

```mermaid
graph TD
    A[Start] --> B{Decision}
```

More text.
"""

    # Create a temporary file for testing
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(test_content)
        temp_path = Path(f.name)

    try:
        # Extract diagrams with position
        diagrams_with_position = extract_diagrams_with_position(temp_path)

        # Should find 1 diagram
        assert len(diagrams_with_position) == 1

        # Check diagram content and position
        diagram, start_pos, end_pos = diagrams_with_position[0]
        assert "graph TD" in diagram
        assert start_pos > 0
        assert end_pos > start_pos

    finally:
        # Clean up temp file
        os.unlink(temp_path)


def test_empty_markdown():
    """Test with empty or non-Mermaid Markdown content."""
    test_content = "# Just a regular document\n\nNo diagrams here."

    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(test_content)
        temp_path = Path(f.name)

    try:
        diagrams = extract_mermaid_diagrams(temp_path)
        assert len(diagrams) == 0

    finally:
        os.unlink(temp_path)
