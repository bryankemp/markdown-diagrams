# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-03-13

### Added
- Extract Mermaid diagrams from Markdown files
- Render diagrams to PNG, SVG, and PDF via the Mermaid CLI
- Automatic output filenames derived from document headings
- Support for 19 diagram fence types (mermaid, flowchart, sequence, ER, class, state, etc.)
- `markdown-diagrams extract` CLI command with options for output directory, format, dimensions, and theme
- Python API: `extract_diagrams`, `render_mermaid_diagram`, and related helpers
- External dependency checker with platform-aware installation instructions
- Sphinx documentation with ReadTheDocs integration
