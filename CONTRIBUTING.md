# Contributing to markdown-diagrams

Thank you for considering contributing! Here's how to get started.

## Development Setup

```bash
git clone https://github.com/bryankemp/markdown-diagrams.git
cd markdown-diagrams
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

## Running Tests

```bash
pytest
```

## Code Style

This project uses **black** for formatting and **ruff** for linting.
Please run both before submitting a pull request:

```bash
black .
ruff check .
```

## Submitting Changes

1. Fork the repository and create a feature branch from `main`.
2. Make your changes and add or update tests as needed.
3. Ensure all tests pass and linting is clean.
4. Open a pull request with a clear description of the change.

## Reporting Issues

Please use the [GitHub issue tracker](https://github.com/bryankemp/markdown-diagrams/issues)
to report bugs or request features. Include steps to reproduce, expected
behavior, and your environment (OS, Python version, Mermaid CLI version).
