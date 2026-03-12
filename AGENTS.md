# Agent Development Guidelines

## Build, Lint, Test Commands

### Setup
```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install development dependencies
pip install -r requirements-dev.txt

# Install project in development mode
pip install -e .
```

### Running Tests
```bash
# Run all tests
pytest tests/

# Run a specific test file
pytest tests/test_extractors.py

# Run a specific test function
pytest tests/test_extractors.py::test_extract_diagrams

# Run tests with coverage
pytest --cov=src tests/

# Run tests with verbose output
pytest -v tests/
```

### Linting and Formatting
```bash
# Check code style with flake8
flake8 src/

# Check code style with pylint
pylint src/

# Auto-format with black
black src/

# Check type hints with mypy
mypy src/
```

## Code Style Guidelines

### Imports
- Use absolute imports when possible
- Group imports in order: standard library, third-party, local
- Import modules, not individual functions when possible
- Use `from module import *` only when necessary for API consistency

### Naming Conventions
- Variables and functions: snake_case
- Classes: PascalCase
- Constants: UPPER_CASE
- Private methods: underscore_prefix

### Type Hints
- Use type hints for all function parameters and return values
- Use typing module for complex types
- Include TypeVar for generic functions
- Use Union for optional types

### Error Handling
- Use specific exceptions rather than generic ones
- Log errors appropriately using the logging module
- Handle file I/O errors explicitly
- Gracefully handle unsupported diagram types
- Always include try/except blocks for critical operations

### Documentation
- Add docstrings to all functions and classes using Google style
- Document parameters with types and descriptions
- Document return values
- Use type hints alongside docstrings where appropriate

### Code Organization
- Keep functions focused and small
- Split large modules into smaller logical components
- Use descriptive variable names
- Avoid magic numbers and strings
- Prefer composition over inheritance where reasonable
- Follow the single responsibility principle

### Testing
- Write unit tests for all functions
- Test edge cases and error conditions
- Use pytest fixtures for common setup operations
- Include both positive and negative test cases
- Test with temporary files for file operations

## File Structure Guidelines

### Source Code Location
All source code should be in the `src/` directory
- `main.py`: CLI entry point
- `extractors.py`: Diagram extraction functionality  
- `renderers.py`: Rendering functionality (to be implemented)

### Documentation
Documentation should be in the `docs/` directory with Sphinx configuration
- Use reStructuredText format
- Include API documentation
- Write usage examples

### Testing
Tests should be in the `tests/` directory with pytest structure:
- Each module should have corresponding test file
- Test files should start with `test_`
- Use descriptive test function names