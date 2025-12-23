#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""TO-DO tracker hook.

Tracks `TODO`/`FIXME` comments added or removed in files.
Runs on PostToolUse for Write/Edit operations.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent.parent))
from hook_logging import hook_invocation


# Combined regex for TODO comments (16x faster than multi-pattern approach)
_TODO_RE = re.compile(
    r"(?:#|//|/\*|<!--)\s*(TODO|FIXME|HACK|XXX|BUG|NOTE)[\s:]+(.+?)(?:\*/|-->|$)",
    re.IGNORECASE,
)

LOG_DIR = Path.home() / ".claude" / "todo-logs"


def extract_todos(content: str) -> list[tuple[str, str, int]]:
    """Extract TODO comments from content.

    Returns list of (type, message, line_number).
    """
    todos = []
    for i, line in enumerate(content.splitlines(), 1):
        match = _TODO_RE.search(line)
        if match:
            todos.append((match.group(1).upper(), match.group(2).strip(), i))
    return todos


def compare_todos(
    old_todos: list[tuple[str, str, int]], new_todos: list[tuple[str, str, int]]
) -> tuple[list[tuple[str, str, int]], list[tuple[str, str, int]]]:
    """Compare old and new TO-DOs.

    Returns (added, removed).
    """
    # Use (type, message) as key, ignoring line numbers
    old_set = {(t, m) for t, m, _ in old_todos}
    new_set = {(t, m) for t, m, _ in new_todos}

    added = [(t, m, ln) for t, m, ln in new_todos if (t, m) not in old_set]
    removed = [(t, m, ln) for t, m, ln in old_todos if (t, m) not in new_set]

    return added, removed


def log_todo_changes(
    file_path: str,
    added: list[tuple[str, str, int]],
    removed: list[tuple[str, str, int]],
) -> None:
    """Log TODO changes to daily file."""
    if not added and not removed:
        return

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOG_DIR / f"todos_{datetime.now():%Y%m%d}.jsonl"

    record = {
        "timestamp": datetime.now().isoformat(),
        "file": file_path,
        "added": [{"type": t, "message": m, "line": ln} for t, m, ln in added],
        "removed": [{"type": t, "message": m, "line": ln} for t, m, ln in removed],
    }

    with log_file.open("a") as f:
        f.write(json.dumps(record) + "\n")


def main() -> None:
    with hook_invocation("todo_tracker") as inv:
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
        new_content = tool_input.get("content", "")

        if not file_path:
            sys.exit(0)

        path = Path(file_path)

        # Skip non-code files
        code_extensions = {
            ".py",
            ".js",
            ".ts",
            ".tsx",
            ".jsx",
            ".go",
            ".rs",
            ".java",
            ".c",
            ".cpp",
            ".h",
            ".md",
        }
        if path.suffix.lower() not in code_extensions:
            sys.exit(0)

        # Get old content if file exists
        old_content = ""
        if path.exists():
            try:
                old_content = path.read_text()
            except OSError:
                pass

        # For Edit operations, new_content might be partial
        # Read the actual new content from the file
        if tool_name == "Edit" and path.exists():
            try:
                new_content = path.read_text()
            except OSError:
                pass

        old_todos = extract_todos(old_content)
        new_todos = extract_todos(new_content)
        added, removed = compare_todos(old_todos, new_todos)

        # Log changes
        log_todo_changes(file_path, added, removed)

        # Report to user
        if added:
            print(f"[Progress] TODOs added in {path.name}:", file=sys.stderr)
            for todo_type, message, line in added:
                print(f"  L{line} [{todo_type}] {message[:60]}", file=sys.stderr)

        if removed:
            print(f"[Success] TODOs resolved in {path.name}:", file=sys.stderr)
            for todo_type, message, _ in removed:
                print(f"  [{todo_type}] {message[:60]}", file=sys.stderr)

        sys.exit(0)


if __name__ == "__main__":
    main()
