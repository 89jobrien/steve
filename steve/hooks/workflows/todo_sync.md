---
name: todo-sync
description: PostToolUse hook for TodoWrite - syncs todos to joedb SQLite database
author: Joseph OBrien
status: unpublished
updated: 2025-12-23
version: 1.0.1
tag: hook
---
# Todo Sync

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""
PostToolUse hook for TodoWrite - syncs Claude's todos to joedb SQLite database.

This hook captures TodoWrite tool calls and syncs them to the local joedb todo system.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

# Add hooks root to path
HOOKS_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(HOOKS_ROOT))

from hook_logging import hook_invocation  # noqa: E402


def sync_todos_to_joedb(todos: list[dict]) -> tuple[int, int]:
    """
    Sync todos to joedb.

    Returns tuple of (synced_count, error_count).
    """
    synced = 0
    errors = 0

    for todo in todos:
        content = todo.get("content", "")
        status = todo.get("status", "pending")

        if not content:
            continue

        # Skip completed todos - we only add new/pending ones
        if status == "completed":
            continue

        # Build joedb command
        cmd = [
            "joedb", "todo", "add",
            content,
            "--project", "claude-session",
            "--tags", f"claude,{status}"
        ]

        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                synced += 1
            else:
                errors += 1
        except (subprocess.TimeoutExpired, FileNotFoundError):
            errors += 1

    return synced, errors


def main() -> int:
    """Main hook entry point."""
    with hook_invocation("todo_sync"):
        # Get tool input from environment
        tool_input_str = os.environ.get("CLAUDE_TOOL_INPUT", "{}")

        try:
            tool_input = json.loads(tool_input_str)
        except json.JSONDecodeError:
            return 0

        todos = tool_input.get("todos", [])

        if not todos:
            return 0

        # Filter to only in_progress and pending todos
        active_todos = [t for t in todos if t.get("status") in ("pending", "in_progress")]

        if not active_todos:
            return 0

        synced, errors = sync_todos_to_joedb(active_todos)

        # Output for Claude to see
        if synced > 0:
            print(f"Synced {synced} todo(s) to joedb", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
```
