#!/usr/bin/env python3
"""
CLI tool for extracting and rendering Mermaid diagrams from Markdown files.
"""

import click
from pathlib import Path
from .extractors import extract_mermaid_diagrams


@click.group()
def cli():
    """Extract and render Mermaid diagrams from Markdown files."""
    pass


@cli.command()
@click.argument("markdown_file", type=click.Path(exists=True))
@click.option(
    "--output-dir", "-o", default=".", help="Output directory for rendered diagrams"
)
def extract(markdown_file, output_dir):
    """Extract Mermaid diagrams from a Markdown file."""
    input_path = Path(markdown_file)
    output_path = Path(output_dir)

    click.echo(f"Extracting diagrams from {input_path}")

    # Extract diagrams
    diagrams = extract_mermaid_diagrams(input_path)

    click.echo(f"Found {len(diagrams)} diagrams")

    # Render each diagram (future implementation)
    for i, diagram in enumerate(diagrams):
        # This would be the rendering functionality
        click.echo(f"Diagram {i + 1}: {diagram[:50]}...")


if __name__ == "__main__":
    cli()
