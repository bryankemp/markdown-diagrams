# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- `validate` CLI command to check Mermaid diagram syntax and optionally auto-fix issues (`--fix`, `--dry-run`)
- Diagram validation API: `validate_diagram`, `fix_diagram`, `validate_and_fix_diagrams`
- External dependency checker with platform-aware installation instructions

### Improved
- Output filenames now prefer bold-text titles (`**...**`) above code fences over generic section headings, producing much more descriptive names (e.g. `flowchart_license_injection_process.png` instead of `diagrams.png`)

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
