"""
markdown-diagrams - Mermaid Diagram Extractor and Renderer

Extract Mermaid diagrams from Markdown files and render them to various
image formats (PNG, SVG, PDF).

Modules:
    extractors: Extract diagrams from Markdown files.
    renderers: Render diagrams to PNG, SVG, and PDF formats.
"""

__version__ = "1.0.0"
__author__ = "Bryan Kemp"

# Import the main functions for easy access
from .extractors import (
    extract_diagrams,
    extract_diagrams_with_position,
    extract_mermaid_diagrams,
)
from .renderers import (
    render_mermaid_diagram,
    render_mermaid_to_pdf,
    render_mermaid_to_png,
    render_mermaid_to_svg,
    sanitize_mermaid_content,
)
from .validators import (
    ValidationResult,
    fix_diagram,
    validate_and_fix_diagrams,
    validate_diagram,
)

__all__ = [
    "extract_diagrams",
    "extract_mermaid_diagrams",
    "extract_diagrams_with_position",
    "render_mermaid_diagram",
    "render_mermaid_to_png",
    "render_mermaid_to_svg",
    "render_mermaid_to_pdf",
    "sanitize_mermaid_content",
    "ValidationResult",
    "validate_diagram",
    "fix_diagram",
    "validate_and_fix_diagrams",
]
