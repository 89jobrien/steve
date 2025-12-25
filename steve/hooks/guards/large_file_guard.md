---
name: large-file-guard
description: Large file guard hook.
author: Joseph OBrien
status: unpublished
updated: 2025-12-23
version: 1.0.1
tag: hook
---
# Large File Guard

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Large file guard hook.

Warns before writing files larger than a threshold (default 100KB).
Runs on PreToolUse for Write/Edit operations.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from hook_logging import hook_invocation

# Size thresholds in bytes
WARN_THRESHOLD = 100 * 1024  # 100KB - warn
BLOCK_THRESHOLD = 1024 * 1024  # 1MB - block

# File patterns to always allow (build outputs, etc.)
ALLOWED_PATTERNS = {
    ".lock",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "poetry.lock",
    "Cargo.lock",
    "uv.lock",
}


def format_size(size: int) -> str:
    """Format size in human-readable format."""
    if size < 1024:
        return f"{size} bytes"
    elif size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    else:
        return f"{size / (1024 * 1024):.1f} MB"


def is_allowed_file(file_path: str) -> bool:
    """Check if file is in the allowed list."""
    path = Path(file_path)
    return path.name in ALLOWED_PATTERNS or path.suffix in ALLOWED_PATTERNS


def main() -> None:
    with hook_invocation("large_file_guard") as inv:
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
        content = tool_input.get("content", "")

        if not file_path or not content:
            sys.exit(0)

        # Skip allowed files
        if is_allowed_file(file_path):
            sys.exit(0)

        content_size = len(content.encode("utf-8"))

        if content_size >= BLOCK_THRESHOLD:
            print(
                f"[Error] File too large: {format_size(content_size)} "
                f"(limit: {format_size(BLOCK_THRESHOLD)})",
                file=sys.stderr,
            )
            print(f"  File: {file_path}", file=sys.stderr)
            print("\nHint: Consider splitting large files or using external storage.", file=sys.stderr)
            sys.exit(2)

        if content_size >= WARN_THRESHOLD:
            print(
                f"[Warning] Large file: {format_size(content_size)} - {Path(file_path).name}",
                file=sys.stderr,
            )

        sys.exit(0)


if __name__ == "__main__":
    main()
```
