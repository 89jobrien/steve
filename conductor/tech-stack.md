# Technology Stack

## Core Language and Runtime
- **Python 3.12+**: The primary programming language for all management scripts, helper modules, and hooks.

## Package and Environment Management
- **UV**: Used for high-performance dependency resolution, environment isolation, and script execution.

## Core Libraries
- **Pydantic**: For robust data validation and settings management.
- **PyYAML**: For parsing and generating component metadata in YAML frontmatter.
- **Requests**: For interacting with the GitHub Gist API and other external services.

## Development and Quality Tools
- **Ruff**: The primary linter and formatter to ensure consistent code style.
- **MyPy**: For static type checking and ensuring type safety across the Python codebase.
- **Pytest**: The framework for running unit and integration tests.
- **Pre-commit**: For automating code quality checks before commits.

## Infrastructure and Distribution
- **GitHub Gists**: Used as the primary distribution mechanism for installing components into Claude Code.
