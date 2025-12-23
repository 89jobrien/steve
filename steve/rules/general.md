---
paths:
- '**/*.json'
- '**/*.md'
- '**/*.sh'
- '**/*.py'
- '**/*.yaml'
- '**/*.yml'
- '**/*.toml'
- '**/*.ts'
- '**/*.tsx'
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: rule
---

# General Rules

Applies to all files in this project.

## Environment

- No vanilla Python on PATH - always use `uv run` for Python operations
- Use `uv` for package management, never pip directly

## Code Style

- No emojis in code or documentation unless explicitly requested
- Prefer editing existing files over creating new ones
- Remove unused code completely, don't comment it out
- Never use emojis in code or documentation unless explicitly requested

## Git

- Never commit secrets, credentials, or API keys
- Atomic, focused commits

## File Patterns

- `*.local.md` - personal notes, gitignored
- `CLAUDE.md` - project instructions for Claude
- `TO-DO.md` - task tracking
- `TO-FIX.md` - issues to fix
