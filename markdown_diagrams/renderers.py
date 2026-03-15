"""
Mermaid Diagram Renderer

This module provides functionality to render Mermaid diagrams to various image formats,
including PNG, SVG, and PDF.
"""

import logging
import os
import re
import subprocess
import tempfile
from pathlib import Path
from typing import Optional

from .dependencies import MERMAID_CLI, check_dependency, format_missing_message

# Set up logging
logger = logging.getLogger(__name__)


def _sanitize_mermaid_content(content: str) -> str:
    """Sanitize Mermaid diagram content to prevent common parse errors.

    In flowchart/graph diagrams, parentheses inside square-bracket node
    labels (e.g. ``A[call foo(x)]``) or diamond node labels
    (e.g. ``B{Check pool (available)?}``) are misinterpreted by the
    Mermaid parser as alternative node-shape markers.  This function
    wraps such labels in double quotes so they are treated as plain text.

    Args:
        content: Raw Mermaid diagram source.

    Returns:
        Sanitized Mermaid source safe for rendering.
    """
    lines = content.strip().split("\n")
    if not lines:
        return content

    first_line = lines[0].strip().lower()
    if not (first_line.startswith("flowchart") or first_line.startswith("graph")):
        return content

    def _quote_bracket_label(match: re.Match) -> str:
        text = match.group(1)
        # Skip compound shape markers: [(db)], [/parallelogram/], [\reverse\]
        if text.startswith(("(", "/", "\\")):
            return match.group(0)
        if "(" in text or ")" in text:
            return f'["{text}"]'
        return match.group(0)

    def _quote_diamond_label(match: re.Match) -> str:
        text = match.group(1)
        if "(" in text or ")" in text:
            return f'{{"{text}"}}'
        return match.group(0)

    def _quote_edge_label(match: re.Match) -> str:
        text = match.group(1)
        if "(" in text or ")" in text:
            return f'|"{text}"|'
        return match.group(0)

    # Quote square-bracket labels: [text with (parens)]
    content = re.sub(r'\[([^\]"]+)\]', _quote_bracket_label, content)
    # Quote diamond labels: {text with (parens)} but not {{hexagon}}
    content = re.sub(r'(?<!\{)\{([^\}"]+)\}(?!\})', _quote_diamond_label, content)
    # Quote edge labels: -->|text with (parens)|
    content = re.sub(r'\|([^|"]+)\|', _quote_edge_label, content)
    return content


def sanitize_mermaid_content(content: str) -> str:
    """Public alias for :func:`_sanitize_mermaid_content`.

    Sanitize Mermaid diagram content to prevent common parse errors.
    See :func:`_sanitize_mermaid_content` for full documentation.

    Args:
        content: Raw Mermaid diagram source.

    Returns:
        Sanitized Mermaid source safe for rendering.
    """
    return _sanitize_mermaid_content(content)


def check_mermaid_cli() -> bool:
    """Check if Mermaid CLI is available.

    Returns:
        True if Mermaid CLI (``mmdc``) is found on ``$PATH``.
    """
    return check_dependency(MERMAID_CLI).available


def render_mermaid_to_png(
    mermaid_content: str,
    output_path: str,
    width: int = 800,
    height: int = 600,
    theme: str = "default",
) -> bool:
    """
    Render a Mermaid diagram to PNG format.

    Args:
        mermaid_content (str): The Mermaid diagram content
        output_path (str): Path where the PNG will be saved
        width (int): Width of the output image
        height (int): Height of the output image
        theme (str): Mermaid theme ('default', 'dark', 'forest')

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Check if Mermaid CLI is available
        status = check_dependency(MERMAID_CLI)
        if not status.available:
            logger.error(format_missing_message(status))
            return False

        # Sanitize content before rendering
        mermaid_content = _sanitize_mermaid_content(mermaid_content)

        # Create a temporary file for the Mermaid diagram
        with tempfile.NamedTemporaryFile(mode="w", suffix=".mmd", delete=False) as f:
            f.write(mermaid_content)
            temp_mmd_file = f.name

        # Configure the output format and size
        cmd = [
            "mmdc",
            "-i",
            temp_mmd_file,
            "-o",
            output_path,
            "-w",
            str(width),
            "-H",
            str(height),
        ]

        # Add theme if specified
        if theme and theme != "default":
            cmd.extend(["-t", theme])

        # Execute the command
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)

        # Clean up the temporary file
        os.unlink(temp_mmd_file)

        if result.returncode == 0:
            logger.info(f"Successfully rendered Mermaid diagram to {output_path}")
            return True
        else:
            logger.error(f"Failed to render Mermaid diagram: {result.stderr}")
            return False

    except Exception as e:
        logger.error(f"Error rendering Mermaid diagram: {e}")
        return False


def render_mermaid_to_svg(
    mermaid_content: str,
    output_path: str,
    width: int = 800,
    height: int = 600,
    theme: str = "default",
) -> bool:
    """
    Render a Mermaid diagram to SVG format.

    Args:
        mermaid_content (str): The Mermaid diagram content
        output_path (str): Path where the SVG will be saved
        width (int): Width of the output image
        height (int): Height of the output image
        theme (str): Mermaid theme ('default', 'dark', 'forest')

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        status = check_dependency(MERMAID_CLI)
        if not status.available:
            logger.error(format_missing_message(status))
            return False

        mermaid_content = _sanitize_mermaid_content(mermaid_content)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".mmd", delete=False) as f:
            f.write(mermaid_content)
            temp_mmd_file = f.name

        cmd = [
            "mmdc",
            "-i",
            temp_mmd_file,
            "-o",
            output_path,
            "-w",
            str(width),
            "-H",
            str(height),
        ]

        if theme and theme != "default":
            cmd.extend(["-t", theme])

        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        os.unlink(temp_mmd_file)

        if result.returncode == 0:
            logger.info(f"Successfully rendered Mermaid diagram to {output_path}")
            return True
        else:
            logger.error(f"Failed to render Mermaid diagram: {result.stderr}")
            return False

    except Exception as e:
        logger.error(f"Error rendering Mermaid diagram: {e}")
        return False


def render_mermaid_to_pdf(
    mermaid_content: str, output_path: str, theme: str = "default"
) -> bool:
    """
    Render a Mermaid diagram to PDF format.

    Args:
        mermaid_content (str): The Mermaid diagram content
        output_path (str): Path where the PDF will be saved
        theme (str): Mermaid theme ('default', 'dark', 'forest')

    Returns:
        bool: True if successful, False otherwise
    """
    try:
        status = check_dependency(MERMAID_CLI)
        if not status.available:
            logger.error(format_missing_message(status))
            return False

        mermaid_content = _sanitize_mermaid_content(mermaid_content)

        with tempfile.NamedTemporaryFile(mode="w", suffix=".mmd", delete=False) as f:
            f.write(mermaid_content)
            temp_mmd_file = f.name

        cmd = [
            "mmdc",
            "-i",
            temp_mmd_file,
            "-o",
            output_path,
        ]

        if theme and theme != "default":
            cmd.extend(["-t", theme])

        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        os.unlink(temp_mmd_file)

        if result.returncode == 0:
            logger.info(f"Successfully rendered Mermaid diagram to {output_path}")
            return True
        else:
            logger.error(f"Failed to render Mermaid diagram: {result.stderr}")
            return False

    except Exception as e:
        logger.error(f"Error rendering Mermaid diagram: {e}")
        return False


def render_mermaid_diagram(
    mermaid_content: str,
    output_dir: str,
    format_type: str = "png",
    width: int = 800,
    height: int = 600,
    theme: str = "default",
    name: Optional[str] = None,
) -> Optional[str]:
    """Render a Mermaid diagram to the specified format.

    Args:
        mermaid_content (str): The Mermaid diagram content.
        output_dir (str): Directory where the output image will be saved.
        format_type (str): Output format ('png', 'svg', 'pdf').
        width (int): Width of the output image.
        height (int): Height of the output image.
        theme (str): Mermaid theme ('default', 'dark', 'forest').
        name (str): Optional filename stem. Falls back to a content hash.

    Returns:
        str: Path to the rendered file or None if failed.
    """
    try:
        # Create output directory if it doesn't exist
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        # Generate filename from provided name or content hash
        if name:
            filename = f"{name}.{format_type}"
        else:
            import hashlib

            content_hash = hashlib.md5(mermaid_content.encode()).hexdigest()[:8]
            filename = f"diagram_{content_hash}.{format_type}"
        output_path = os.path.join(output_dir, filename)

        # Choose the appropriate rendering function
        if format_type.lower() == "png":
            success = render_mermaid_to_png(
                mermaid_content, output_path, width, height, theme
            )
        elif format_type.lower() == "svg":
            success = render_mermaid_to_svg(
                mermaid_content, output_path, width, height, theme
            )
        elif format_type.lower() == "pdf":
            success = render_mermaid_to_pdf(mermaid_content, output_path, theme)
        else:
            logger.error(f"Unsupported format: {format_type}")
            return None

        return output_path if success else None

    except Exception as e:
        logger.error(f"Error rendering Mermaid diagram: {e}")
        return None


def get_mermaid_version() -> Optional[str]:
    """
    Get the version of the Mermaid CLI tool if available.

    Returns:
        str: Version string or None if not available
    """
    try:
        result = subprocess.run(
            ["mmdc", "--version"], capture_output=True, text=True, check=False
        )
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except Exception:
        return None
