#!/usr/bin/env python3
"""
CLI tool for extracting and rendering Mermaid diagrams from Markdown files.
"""

import click
from pathlib import Path
from .extractors import extract_diagrams, extract_mermaid_diagrams
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
def extract(markdown_file, output_dir, diagram_types):
    """Extract diagrams from a Markdown file."""
    input_path = Path(markdown_file)
    output_path = Path(output_dir)

    try:
        click.echo(f"Extracting diagrams from {input_path}")

        # If no diagram types specified, extract all supported types
        if not diagram_types:
            diagram_types = None

        # Extract diagrams
        all_diagrams = extract_diagrams(input_path, diagram_types)

        # Count and display results
        total_count = sum(len(diagrams) for diagrams in all_diagrams.values())
        click.echo(f"Found {total_count} diagrams total")

        # Display each diagram type and count
        for diagram_type, diagrams in all_diagrams.items():
            if diagrams:
                click.echo(f"  {diagram_type}: {len(diagrams)} found")
                for i, diagram in enumerate(diagrams):
                    click.echo(f"    {diagram_type} {i + 1}: {diagram[:100]}")
            else:
                click.echo(f"  {diagram_type}: 0 found")

    except Exception as e:
        logger.error(f"Error processing {input_path}: {str(e)}")
        raise click.Abort()


if __name__ == "__main__":
    cli()
