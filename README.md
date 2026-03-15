# markdown-diagrams

Extract and render [Mermaid](https://mermaid.js.org/) diagrams from Markdown files to PNG, SVG, and PDF.

## Features

- Extract Mermaid diagrams from any Markdown file
- Render diagrams to PNG, SVG, and PDF formats
- Automatically name output files based on document headings
- Support for 19 diagram types (flowchart, sequence, ER, class, state, gantt, and more)
- Extensible architecture for additional diagram types

## Prerequisites

Rendering requires the [Mermaid CLI](https://github.com/mermaid-js/mermaid-cli):

```bash
npm install -g @mermaid-js/mermaid-cli
```

## Installation

### From PyPI

```bash
pip install markdown-diagrams
```

### From source

```bash
git clone https://github.com/bryankemp/markdown-diagrams.git
cd markdown-diagrams
pip install -e .
```

## Usage

### Extract and render all diagrams

```bash
markdown-diagrams extract document.md
```

### Specify an output directory

```bash
markdown-diagrams extract document.md -o ./output
```

### Filter by diagram type

```bash
markdown-diagrams extract document.md -t mermaid -t flowchart
```

### Choose an output format

```bash
# PNG (default)
markdown-diagrams extract document.md -f png

# SVG
markdown-diagrams extract document.md -f svg

# PDF
markdown-diagrams extract document.md -f pdf
```

### Custom dimensions and theme

```bash
markdown-diagrams extract document.md -w 1000 -H 800 -T dark
```

## Supported Diagram Types

`mermaid` · `flowchart` · `sequence` · `graph` · `gantt` · `pie` · `mindmap` ·
`quadrantDiagram` · `er` · `class` · `state` · `journey` · `gitGraph` ·
`userJourney` · `requirement` · `c4` · `entityRelationship` · `component` · `active`

## Python API

```python
from markdown_diagrams import extract_diagrams, render_mermaid_diagram
from pathlib import Path

# Extract diagrams
diagrams = extract_diagrams(Path("document.md"))
for diagram_type, items in diagrams.items():
    for item in items:
        print(f"[{diagram_type}] {item['heading']}: {len(item['content'])} chars")

# Render a single diagram
render_mermaid_diagram(items[0]["content"], output_dir="./output")
```

## Development

```bash
pip install -e ".[dev]"
pytest
black --check .
ruff check .
```

## Documentation

Full documentation is available at [markdown-diagrams.readthedocs.io](https://markdown-diagrams.readthedocs.io).

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

BSD 3-Clause License — see [LICENSE](LICENSE) for details.
