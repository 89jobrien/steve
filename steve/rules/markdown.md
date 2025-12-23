---
paths: '**/*.md'
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: rule
---

# Markdown Rules

## Formatting

- Line length: 120 characters max
- Use fenced code blocks with language identifier (```python,```bash)
- No trailing whitespace

## Auto-formatting

A PostToolUse hook runs prettier and markdownlint on save. Config files:

- `.prettierrc` - formatting rules
- `.markdownlint.json` - linting rules

## Allowed HTML

Only these elements are permitted: `<details>`, `<summary>`, `<br>`, `<sup>`, `<sub>`

## Headers

- Use ATX-style (`#` prefix), not underlines
- No first-line heading requirement (MD041 disabled)

## General

- Never use emojis in code or documentation unless explicitly requested
- Prefer editing existing files over creating new ones

## Examples

### Code Blocks

All code blocks should be fenced with ``` and the language identifier.

```python
import os
print(os.getcwd())
```

The language should be specified and, if not necessary, it should be specified as 'text'.

```text
This is a text block.
It can be used for trees, outputs, etc.
```
