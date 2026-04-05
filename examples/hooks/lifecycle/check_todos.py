#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///

"""Validate todo completions before stop.

This hook checks for incomplete TODOs in the transcript before allowing stop.
Runs on Stop and SubagentStop events.
"""

import json
import re
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent.parent))
from hook_logging import hook_invocation


MAX_TRANSCRIPT_SIZE = 10 * 1024 * 1024


def find_incomplete_todos(transcript_data: dict) -> list[str]:
    incomplete: list[str] = []

    if not isinstance(transcript_data, dict):
        return []

    messages = transcript_data.get("messages", [])
    if not isinstance(messages, list):
        return incomplete

    todo_pattern = r"(?:TODO|FIXME|XXX):\s*(.+)"
    completed_pattern = r"(?:DONE|COMPLETED|FIXED):\s*(.+)"

    todos = set()
    completed = set()

    for message in messages:
        if not isinstance(message, dict):
            continue

        content = message.get("content", "")
        if isinstance(content, list):
            for item in content:
                if isinstance(item, dict) and item.get("type") == "text":
                    text = item.get("text", "")
                    todos.update(re.findall(todo_pattern, text, re.IGNORECASE))
                    completed.update(re.findall(completed_pattern, text, re.IGNORECASE))
        elif isinstance(content, str):
            todos.update(re.findall(todo_pattern, content, re.IGNORECASE))
            completed.update(re.findall(completed_pattern, content, re.IGNORECASE))

    incomplete = [todo for todo in todos if todo not in completed]
    return incomplete


def main() -> None:
    with hook_invocation("check_todos") as inv:
        try:
            payload = json.load(sys.stdin)
        except json.JSONDecodeError:
            sys.exit(0)

        inv.set_payload(payload)

        if payload.get("stop_hook_active"):
            sys.exit(0)

        transcript_path = payload.get("transcript_path")
        if not transcript_path:
            sys.exit(0)

        path = Path(transcript_path)
        if not path.exists():
            sys.exit(0)

        try:
            content = path.read_text(encoding="utf-8")
            if len(content) > MAX_TRANSCRIPT_SIZE:
                print(
                    "[Warning] Transcript file too large, skipping check",
                    file=sys.stderr,
                )
                sys.exit(0)
            transcript_data = json.loads(content)
        except (OSError, json.JSONDecodeError):
            sys.exit(0)

        incomplete_todos = find_incomplete_todos(transcript_data)

        if incomplete_todos:
            print("[Error] Incomplete todos found", file=sys.stderr)
            print(
                f"  Details: Found {len(incomplete_todos)} incomplete todo(s)",
                file=sys.stderr,
            )
            print("  Hints:", file=sys.stderr)
            print("    - Complete all todos before stopping", file=sys.stderr)
            print("    - Remove todos that are no longer needed", file=sys.stderr)
            print("    - Update todo status to completed", file=sys.stderr)

            for todo in incomplete_todos:
                print(f"  [ ] {todo}", file=sys.stderr)

            sys.exit(1)

        sys.exit(0)


if __name__ == "__main__":
    main()
