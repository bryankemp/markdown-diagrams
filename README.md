# Ursula

A tool for extracting and rendering Mermaid diagrams from Markdown files.

## Features

- Extract Mermaid diagrams from Markdown files
- Render diagrams to PNG format
- Command-line interface for easy usage

## Installation

```bash
pip install .
```

## Usage

```bash
# Extract diagrams from a Markdown file
ursula extract input.md

# Extract diagrams and save to a specific directory
ursula extract input.md --output-dir ./output
```

## Development

To install in development mode:

```bash
pip install -e .
```

## Testing

Run tests with pytest:

```bash
pytest tests/
```