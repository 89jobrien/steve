---
paths: '**/*.toml'
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: rule
---

# TOML Rules

## pyproject.toml

- Use `uv add` to manage dependencies, don't edit manually
- Keep `[project.scripts]` for CLI entry points
- Configure tools (ruff, pytest) in their respective sections
