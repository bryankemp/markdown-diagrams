#!/usr/bin/env python3
"""
Mermaid Diagram Validator and Auto-fixer

Provides validation of Mermaid diagrams via the Mermaid CLI (mmdc) and
heuristic auto-fixing of common syntax issues, with optional write-back
of fixes to the source Markdown file.
"""

import logging
import os
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Tuple

from .dependencies import MERMAID_CLI, check_dependency, format_missing_message
from .extractors import _find_preceding_heading, extract_diagrams_with_position
from .renderers import sanitize_mermaid_content

# Set up logging
logger = logging.getLogger(__name__)


@dataclass
class ValidationResult:
    """Result of validating a single Mermaid diagram."""

    index: int
    """1-based position of the diagram within the file."""

    heading: Optional[str]
    """Nearest preceding Markdown heading, or ``None``."""

    content: str
    """Original diagram source text."""

    valid: bool
    """``True`` if mmdc accepted the diagram without errors."""

    errors: List[str] = field(default_factory=list)
    """List of error messages returned by mmdc (empty when valid)."""

    fixed_content: Optional[str] = None
    """Auto-fixed diagram source, or ``None`` if no changes were needed."""

    start: int = 0
    """Byte offset of the opening mermaid fence in the file."""

    end: int = 0
    """Byte offset immediately after the closing fence."""


def fix_diagram(content: str) -> str:
    """Apply heuristic fixes to Mermaid diagram content.

    Fixes applied (in order):

    1. Normalize line endings (``\\r\\n`` and bare ``\\r`` → ``\\n``).
    2. Strip trailing whitespace from every line.
    3. Strip leading and trailing blank lines.
    4. Quote node labels and edge labels that contain parentheses in
       ``flowchart`` / ``graph`` diagrams (delegates to
       :func:`~markdown_diagrams.renderers.sanitize_mermaid_content`).

    Args:
        content: Raw Mermaid diagram source.

    Returns:
        Fixed Mermaid source.  Returns the original string unchanged if
        no fixes were necessary.
    """
    # Normalize line endings
    content = content.replace("\r\n", "\n").replace("\r", "\n")
    # Strip trailing whitespace from each line
    content = "\n".join(line.rstrip() for line in content.split("\n"))
    # Strip leading/trailing blank lines
    content = content.strip()
    # Apply parentheses-quoting sanitization for flowchart/graph diagrams
    content = sanitize_mermaid_content(content)
    return content


def _parse_mmdc_errors(stderr: str) -> List[str]:
    """Extract meaningful error messages from mmdc stderr output.

    Args:
        stderr: The stderr output captured from an ``mmdc`` invocation.

    Returns:
        List of error message strings.  Empty if no recognisable errors
        are found.
    """
    errors: List[str] = []
    for line in stderr.splitlines():
        line = line.strip()
        if not line:
            continue
        lower = line.lower()
        if (
            lower.startswith("error")
            or "parse error" in lower
            or "syntax error" in lower
            or "unexpected" in lower
        ):
            errors.append(line)
    return errors


def validate_diagram(content: str) -> Tuple[bool, List[str]]:
    """Validate a Mermaid diagram by attempting to render it with mmdc.

    Writes *content* to a temporary ``.mmd`` file, invokes
    ``mmdc -i <input> -o <output>`` in a temporary directory, and
    inspects the exit code and stderr to determine validity.

    If mmdc is not installed the function returns ``(True, [])`` and
    logs a warning rather than treating every diagram as invalid.

    Args:
        content: Mermaid diagram source text.

    Returns:
        A ``(valid, errors)`` tuple where *valid* is ``True`` when mmdc
        exits with code 0 and *errors* is a (possibly empty) list of
        error messages parsed from stderr.
    """
    status = check_dependency(MERMAID_CLI)
    if not status.available:
        logger.warning(
            "mmdc not found — skipping live validation. "
            + format_missing_message(status)
        )
        return True, []

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            input_file = os.path.join(tmpdir, "diagram.mmd")
            output_file = os.path.join(tmpdir, "diagram.png")

            with open(input_file, "w", encoding="utf-8") as f:
                f.write(content)

            result = subprocess.run(
                ["mmdc", "-i", input_file, "-o", output_file],
                capture_output=True,
                text=True,
                check=False,
            )

            if result.returncode == 0:
                return True, []

            errors = _parse_mmdc_errors(result.stderr)
            if not errors:
                raw = result.stderr.strip()
                errors = [raw] if raw else ["Diagram failed to render (unknown error)"]
            return False, errors

    except Exception as exc:
        logger.error(f"Error validating diagram: {exc}")
        return False, [str(exc)]


def validate_and_fix_diagrams(
    markdown_file: Path,
    apply_fixes: bool = False,
) -> List[ValidationResult]:
    """Validate all Mermaid diagrams in a Markdown file.

    For each `````mermaid`` block the function:

    * validates the diagram with :func:`validate_diagram`,
    * computes a fixed version with :func:`fix_diagram` (``fixed_content``
      is set only when the fixed text differs from the original),
    * optionally writes all fixes back to *markdown_file* in a single
      atomic pass (last-to-first to preserve byte offsets).

    Args:
        markdown_file: Path to the source Markdown file.
        apply_fixes: When ``True``, write fixed diagram content back to
            *markdown_file* for every diagram where
            :func:`fix_diagram` produces a different result.

    Returns:
        Ordered list of :class:`ValidationResult`, one per diagram found.
        Returns an empty list when no Mermaid diagrams are present or the
        file cannot be read.
    """
    try:
        content = markdown_file.read_text(encoding="utf-8")
    except Exception as exc:
        logger.error(f"Failed to read {markdown_file}: {exc}")
        return []

    positions = extract_diagrams_with_position(markdown_file, "mermaid")
    if not positions:
        return []

    results: List[ValidationResult] = []
    for index, (diagram_content, start, end) in enumerate(positions, start=1):
        heading = _find_preceding_heading(content, start)
        valid, errors = validate_diagram(diagram_content)

        fixed = fix_diagram(diagram_content)
        fixed_content: Optional[str] = fixed if fixed != diagram_content else None

        results.append(
            ValidationResult(
                index=index,
                heading=heading,
                content=diagram_content,
                valid=valid,
                errors=errors,
                fixed_content=fixed_content,
                start=start,
                end=end,
            )
        )

    if apply_fixes:
        _write_fixes(markdown_file, content, results)

    return results


def _write_fixes(
    markdown_file: Path,
    original_content: str,
    results: List[ValidationResult],
) -> None:
    """Write fixed diagram content back to the Markdown file.

    Replaces code fences from last-to-first position so that earlier
    byte offsets remain valid throughout the pass.

    Args:
        markdown_file: Destination file path.
        original_content: Current content of *markdown_file*.
        results: Validation results that may carry a ``fixed_content``.
    """
    to_fix = sorted(
        [r for r in results if r.fixed_content is not None],
        key=lambda r: r.start,
        reverse=True,
    )

    if not to_fix:
        return

    patched = original_content
    for result in to_fix:
        new_block = f"```mermaid\n{result.fixed_content}\n```"
        patched = patched[: result.start] + new_block + patched[result.end :]

    try:
        markdown_file.write_text(patched, encoding="utf-8")
        logger.info(f"Wrote {len(to_fix)} fix(es) back to {markdown_file}")
    except Exception as exc:
        logger.error(f"Failed to write fixes to {markdown_file}: {exc}")
