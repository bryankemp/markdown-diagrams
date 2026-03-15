#!/usr/bin/env python3
"""
CLI tool for extracting and rendering Mermaid diagrams from Markdown files.
"""

import logging
from pathlib import Path

import click

from .dependencies import check_all, format_missing_message
from .extractors import extract_diagrams, heading_to_filename
from .renderers import render_mermaid_diagram
from .validators import validate_and_fix_diagrams

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def _check_external_tools() -> None:
    """Verify that required external tools are installed.

    Prints a detailed, user-friendly error and exits if any tool is missing.
    """
    statuses = check_all()
    missing = [s for s in statuses if not s.available]
    if missing:
        for status in missing:
            click.echo(format_missing_message(status), err=True)
        raise SystemExit(1)


@click.group()
def cli():
    """Extract and render diagrams from Markdown files."""
    pass


@cli.command()
@click.argument("markdown_file", type=click.Path(exists=True))
@click.option(
    "--output-dir", "-o", default=".", help="Output directory for rendered diagrams"
)
@click.option(
    "--diagram-types",
    "-t",
    multiple=True,
    help="Diagram types to extract (e.g., mermaid, flowchart)",
)
@click.option(
    "--format",
    "-f",
    default="png",
    help="Output format for rendered diagrams (png, svg, pdf)",
)
@click.option("--width", "-w", default=800, help="Width of output images")
@click.option("--height", "-H", default=600, help="Height of output images")
@click.option(
    "--theme", "-T", default="default", help="Mermaid theme (default, dark, forest)"
)
def extract(markdown_file, output_dir, diagram_types, format, width, height, theme):
    """Extract and render diagrams from a Markdown file."""
    _check_external_tools()

    input_path = Path(markdown_file)
    output_path = Path(output_dir)

    try:
        click.echo(f"Extracting and rendering diagrams from {input_path}")

        # If no diagram types specified, extract all supported types
        if not diagram_types:
            diagram_types = None

        # Extract diagrams
        all_diagrams = extract_diagrams(input_path, diagram_types)

        # Count and display results
        total_count = sum(len(diagrams) for diagrams in all_diagrams.values())
        click.echo(f"Found {total_count} diagrams total")

        # Render each diagram type
        used_names: dict[str, int] = {}
        for diagram_type, diagrams in all_diagrams.items():
            if diagrams:
                click.echo(f"  {diagram_type}: {len(diagrams)} found")
                for i, diagram_info in enumerate(diagrams):
                    # Derive a human-readable filename from the heading
                    name = None
                    heading = diagram_info.get("heading")
                    if heading:
                        base = heading_to_filename(heading)
                        count = used_names.get(base, 0)
                        used_names[base] = count + 1
                        name = f"{base}_{count + 1}" if count else base

                    # Render the diagram
                    rendered_file = render_mermaid_diagram(
                        diagram_info["content"],
                        str(output_path),
                        format,
                        width,
                        height,
                        theme,
                        name=name,
                    )
                    if rendered_file:
                        click.echo(
                            f"    Rendered {diagram_type} {i + 1} to {rendered_file}"
                        )
                    else:
                        click.echo(f"    Failed to render {diagram_type} {i + 1}")

    except Exception as e:
        logger.error(f"Error processing {input_path}: {str(e)}")
        raise click.Abort()


@cli.command()
@click.argument("markdown_file", type=click.Path(exists=True))
@click.option(
    "--fix",
    "-F",
    is_flag=True,
    help="Apply auto-fixes and write changes back to the Markdown file.",
)
@click.option(
    "--dry-run",
    "-n",
    is_flag=True,
    help="Show what would be fixed without writing any changes.",
)
def validate(markdown_file, fix, dry_run):
    """Validate Mermaid diagrams and optionally auto-fix issues.

    Exits with code 1 when any diagram has validation errors and --fix was
    not supplied (or when --dry-run is active).
    """
    _check_external_tools()

    if fix and dry_run:
        raise click.UsageError("--fix and --dry-run are mutually exclusive.")

    input_path = Path(markdown_file)
    apply_fixes = fix and not dry_run

    try:
        results = validate_and_fix_diagrams(input_path, apply_fixes=apply_fixes)
    except Exception as e:
        logger.error(f"Error validating {input_path}: {str(e)}")
        raise click.Abort()

    if not results:
        click.echo("No Mermaid diagrams found.")
        return

    invalid_count = 0
    fixable_count = 0

    for r in results:
        heading_label = f" ({r.heading})" if r.heading else ""
        status = "OK  " if r.valid else "FAIL"
        click.echo(f"  [{status}] Diagram {r.index}{heading_label}")

        if not r.valid:
            invalid_count += 1
            for err in r.errors:
                click.echo(f"        {err}", err=True)

        if r.fixed_content is not None:
            fixable_count += 1
            if dry_run:
                click.echo(
                    f"    [dry-run] Diagram {r.index} has fixable formatting issues."
                )

    click.echo("")
    if invalid_count == 0:
        click.echo(f"All {len(results)} diagram(s) are valid.")
    else:
        click.echo(f"{invalid_count}/{len(results)} diagram(s) have validation errors.")

    if apply_fixes:
        if fixable_count > 0:
            click.echo(f"Applied fixes to {fixable_count} diagram(s) in {input_path}.")
        else:
            click.echo("No fixable formatting issues found.")
    elif dry_run and fixable_count > 0:
        click.echo(f"{fixable_count} diagram(s) could be auto-fixed with --fix.")

    if invalid_count > 0 and not apply_fixes:
        raise SystemExit(1)


if __name__ == "__main__":
    cli()
