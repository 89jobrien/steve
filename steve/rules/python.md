---
paths: '**/*.py'
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: rule
---

# Python Rules

## General

- Use Python 3.12 or higher
- Use `uv` for all Python operations
- Never use `pip` directly

## uv-Only Environment

**CRITICAL**: This system has no vanilla Python on PATH. Always use `uv` for all Python operations:

| Instead of | Use |
|------------|-----|
| `python` | `uv run python` |
| `python script.py` | `uv run script.py` |
| `pip install` | `uv add` |
| `pip install -e .` | `uv pip install -e .` |
| `pytest` | `uv run pytest` |
| `ruff` | `uvx ruff` |
| `mypy` | `uvx mypy` |

## Running Scripts

```bash
# Run a Python file
uv run script.py

# Run a module
uv run -m pytest

# Run with specific dependencies
uv run --with requests script.py
```

## Package Management

- Use `uv add <package>` to add dependencies to pyproject.toml
- Use `uv sync` to install from lock file
- Use `uv lock` to update lock file
- Never use `pip` directly

## Style Guide

- Never use emojis in code or documentation unless explicitly requested
- Always use type hints
- Never use print statements for logging
- Always use structured logging
- `typing.List` and `typing.Dict` are deprecated in favor of the built-in `list` and `dict` types
- Never use `typing.Optional`, use `T | None` instead
- Always use `pathlib` for file operations
- Use `SQLModel` for database operations
- Never use `pandas` for data operations, use `polars` instead
- Always use `asyncio` for asynchronous operations
