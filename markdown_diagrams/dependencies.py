"""
External dependency checker for markdown-diagrams.

Verifies that required external tools (e.g. the Mermaid CLI) are installed
and reachable on ``$PATH``, and provides platform-aware installation
instructions when they are not.
"""

import logging
import platform
import shutil
import subprocess
from dataclasses import dataclass, field
from typing import List, Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class Dependency:
    """Description of a single external dependency."""

    name: str
    """Human-readable name (e.g. ``Mermaid CLI``)."""

    command: str
    """Executable name to look up on ``$PATH`` (e.g. ``mmdc``)."""

    version_flag: str = "--version"
    """Flag passed to *command* to retrieve a version string."""

    why: str = ""
    """Short explanation of why this dependency is needed."""

    install_instructions: List[str] = field(default_factory=list)
    """
    Ordered list of installation methods.  Each entry is a human-readable
    string that may contain a shell command (the caller is responsible for
    formatting).
    """

    url: str = ""
    """Project homepage / documentation URL."""


# ---------------------------------------------------------------------------
# Known dependencies
# ---------------------------------------------------------------------------

MERMAID_CLI = Dependency(
    name="Mermaid CLI (mmdc)",
    command="mmdc",
    version_flag="--version",
    why="Required to render Mermaid diagrams to PNG, SVG, and PDF.",
    install_instructions=[
        "npm install -g @mermaid-js/mermaid-cli",
        "yarn global add @mermaid-js/mermaid-cli",
        "brew install mermaid-cli  (macOS with Homebrew)",
    ],
    url="https://github.com/mermaid-js/mermaid-cli",
)

#: Every external tool that markdown-diagrams may need at runtime.
ALL_DEPENDENCIES: List[Dependency] = [MERMAID_CLI]

# ---------------------------------------------------------------------------
# Checking helpers
# ---------------------------------------------------------------------------


@dataclass
class DependencyStatus:
    """Result of checking a single dependency."""

    dependency: Dependency
    available: bool
    version: Optional[str] = None


def check_dependency(dep: Dependency) -> DependencyStatus:
    """Check whether *dep* is installed and return its status.

    Args:
        dep: The dependency to check.

    Returns:
        A ``DependencyStatus`` indicating availability and version.
    """
    path = shutil.which(dep.command)
    if path is None:
        return DependencyStatus(dependency=dep, available=False)

    version: Optional[str] = None
    try:
        result = subprocess.run(
            [dep.command, dep.version_flag],
            capture_output=True,
            text=True,
            check=False,
            timeout=10,
        )
        if result.returncode == 0:
            version = result.stdout.strip() or result.stderr.strip()
    except Exception:
        pass  # We already know the binary exists; version is optional.

    return DependencyStatus(dependency=dep, available=True, version=version)


def check_all() -> List[DependencyStatus]:
    """Check every dependency in :data:`ALL_DEPENDENCIES`.

    Returns:
        List of ``DependencyStatus`` objects, one per dependency.
    """
    return [check_dependency(dep) for dep in ALL_DEPENDENCIES]


# ---------------------------------------------------------------------------
# User-friendly error formatting
# ---------------------------------------------------------------------------


def format_missing_message(status: DependencyStatus) -> str:
    """Return a detailed, user-friendly error message for a missing dependency.

    Args:
        status: A ``DependencyStatus`` where ``available`` is ``False``.

    Returns:
        Multi-line string with the problem description and install options.
    """
    dep = status.dependency
    lines = [
        f"ERROR: {dep.name} is not installed or not found on your PATH.",
        "",
    ]
    if dep.why:
        lines.append(f"  {dep.why}")
        lines.append("")

    lines.append("  To install, try one of the following:")
    lines.append("")
    for instruction in dep.install_instructions:
        lines.append(f"    $ {instruction}")

    current_os = platform.system()
    if current_os == "Darwin":
        lines.append("")
        lines.append("  On macOS you may also need to install Node.js first:")
        lines.append("    $ brew install node")
    elif current_os == "Linux":
        lines.append("")
        lines.append(
            "  On Linux, install Node.js via your package manager or nvm first."
        )
    elif current_os == "Windows":
        lines.append("")
        lines.append("  On Windows, install Node.js from https://nodejs.org/ first.")

    if dep.url:
        lines.append("")
        lines.append(f"  For more details see: {dep.url}")

    return "\n".join(lines)


def require_all(strict: bool = True) -> List[DependencyStatus]:
    """Check all dependencies and optionally raise on missing ones.

    Args:
        strict: If ``True`` (the default), raise ``SystemExit`` when any
            dependency is missing.  If ``False``, just log warnings.

    Returns:
        List of ``DependencyStatus`` objects.

    Raises:
        SystemExit: When *strict* is ``True`` and a dependency is missing.
    """
    statuses = check_all()
    missing = [s for s in statuses if not s.available]

    if not missing:
        return statuses

    for status in missing:
        msg = format_missing_message(status)
        if strict:
            logger.error(msg)
        else:
            logger.warning(msg)

    if strict:
        raise SystemExit(1)

    return statuses
