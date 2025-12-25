---
name: path-validation
description: Path validation hook.
author: Joseph OBrien
status: unpublished
updated: 2025-12-23
version: 1.0.1
tag: hook
---
# Path Validation

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Path validation hook.

Blocks writes outside allowed project directories.
Prevents accidental modifications to system files or other projects.
Runs on PreToolUse for Write/Edit operations.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from hook_logging import hook_invocation

# Directories that are always blocked (system paths)
BLOCKED_PATHS = {
    "/etc",
    "/usr",
    "/bin",
    "/sbin",
    "/var",
    "/System",
    "/Library",
    "/Applications",
}

# Directories that are always allowed
ALLOWED_PATHS = {
    str(Path.home() / ".claude"),  # Claude config
    "/tmp",
    "/private/tmp",
}


def is_path_allowed(file_path: str, cwd: str) -> tuple[bool, str]:
    """Check if the path is allowed for writing.

    Returns (is_allowed, reason).
    """
    try:
        resolved = Path(file_path).expanduser().resolve()
    except (OSError, ValueError):
        return False, "Invalid path"

    resolved_str = str(resolved)

    # Check blocked system paths
    for blocked in BLOCKED_PATHS:
        if resolved_str.startswith(blocked):
            return False, f"System path blocked: {blocked}"

    # Check always-allowed paths
    for allowed in ALLOWED_PATHS:
        if resolved_str.startswith(allowed):
            return True, "Allowed path"

    # Allow paths under current working directory
    try:
        cwd_resolved = Path(cwd).resolve()
        if resolved_str.startswith(str(cwd_resolved)):
            return True, "Under cwd"
    except (OSError, ValueError):
        pass

    # Allow paths under home directory (but warn for paths far from cwd)
    home = str(Path.home())
    if resolved_str.startswith(home):
        return True, "Under home"

    return False, f"Path outside allowed directories: {resolved_str}"


def main() -> None:
    with hook_invocation("path_validation") as inv:
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
        cwd = payload.get("cwd", os.getcwd())

        if not file_path:
            sys.exit(0)

        allowed, reason = is_path_allowed(file_path, cwd)

        if not allowed:
            print(f"[Error] Path validation failed: {reason}", file=sys.stderr)
            print(f"  Attempted path: {file_path}", file=sys.stderr)
            print(f"  Current directory: {cwd}", file=sys.stderr)
            print("\nHint: Only write to project directories or ~/.", file=sys.stderr)
            sys.exit(2)

        sys.exit(0)


if __name__ == "__main__":
    main()
```
