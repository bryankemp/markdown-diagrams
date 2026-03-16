# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2026-03-16

### Added
- Extract Mermaid diagrams from Markdown files
- Render diagrams to PNG, SVG, and PDF via the Mermaid CLI
- Automatic output filenames derived from bold-text titles (`**...**`) above code fences, falling back to document headings
- Support for 19 diagram fence types (mermaid, flowchart, sequence, ER, class, state, gantt, pie, mindmap, gitGraph, journey, quadrantChart, requirement, C4, and more)
- `markdown-diagrams extract` CLI command with options for output directory, format, dimensions, and theme
- `markdown-diagrams validate` CLI command to check diagram syntax with optional auto-fix (`--fix`, `--dry-run`)
- Python API: `extract_diagrams`, `render_mermaid_diagram`, `validate_diagram`, `fix_diagram`, and related helpers
- External dependency checker with platform-aware installation instructions
- Comprehensive example file demonstrating all supported diagram types
- GitHub Actions CI (Python 3.9–3.13) and PyPI publish workflows
- Sphinx documentation with ReadTheDocs integration
