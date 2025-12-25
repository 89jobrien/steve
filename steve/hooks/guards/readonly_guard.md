---
name: readonly-guard
description: Readonly files guard hook.
author: Joseph OBrien
status: unpublished
updated: 2025-12-23
version: 1.0.1
tag: hook
---
# Readonly Guard

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Readonly files guard hook.

Protects lock files, generated files, and vendor directories from modification.
Runs on PreToolUse for Write/Edit operations.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from hook_logging import hook_invocation

# File patterns that should not be manually edited
READONLY_PATTERNS = [
    # Lock files
    r"package-lock\.json$",
    r"yarn\.lock$",
    r"pnpm-lock\.yaml$",
    r"poetry\.lock$",
    r"Cargo\.lock$",
    r"uv\.lock$",
    r"Gemfile\.lock$",
    r"composer\.lock$",
    # Generated files
    r"\.min\.js$",
    r"\.min\.css$",
    r"\.map$",
    r"\.d\.ts$",  # TypeScript declarations (usually generated)
    # Vendor/dependency directories
    r"/node_modules/",
    r"/vendor/",
    r"/__pycache__/",
    r"/\.git/",
    r"/dist/",
    r"/build/",
    r"/\.next/",
    r"/\.nuxt/",
    # IDE/editor files
    r"/\.idea/",
    r"/\.vscode/settings\.json$",  # settings.json specifically
]

# Patterns that are always allowed even if they match above
OVERRIDE_ALLOWED = [
    r"\.vscode/launch\.json$",  # Debug configs are ok
    r"\.vscode/tasks\.json$",  # Task configs are ok
]


def is_readonly(file_path: str) -> tuple[bool, str]:
    """Check if file should be readonly.

    Returns (is_readonly, pattern_matched).
    """
    # Check override patterns first
    for pattern in OVERRIDE_ALLOWED:
        if re.search(pattern, file_path):
            return False, ""

    # Check readonly patterns
    for pattern in READONLY_PATTERNS:
        if re.search(pattern, file_path):
            return True, pattern

    return False, ""


def main() -> None:
    with hook_invocation("readonly_guard") as inv:
        try:
            payload = json.load(sys.stdin)
        except json.JSONDecodeError:
            sys.exit(0)

        inv.set_payload(payload)

        if payload.get("stop_hook_active"):
            sys.exit(0)

        tool_name = payload.get("tool_name")
        if tool_name not in ("Write", "Edit", "MultiEdit"):
            sys.exit(0)

        tool_input = payload.get("tool_input", {})
        if not isinstance(tool_input, dict):
            sys.exit(0)

        file_path = tool_input.get("file_path", "")

        if not file_path:
            sys.exit(0)

        readonly, pattern = is_readonly(file_path)

        if readonly:
            print("[Error] Readonly file protection triggered", file=sys.stderr)
            print(f"  File: {file_path}", file=sys.stderr)
            print(f"  Pattern: {pattern}", file=sys.stderr)
            print("\nHint: This file is auto-generated or managed by tools.", file=sys.stderr)
            print("  - Lock files: Use package manager commands instead", file=sys.stderr)
            print("  - Generated files: Modify source files instead", file=sys.stderr)
            print("  - Vendor dirs: Don't modify dependencies directly", file=sys.stderr)
            sys.exit(2)

        sys.exit(0)


if __name__ == "__main__":
    main()
```
