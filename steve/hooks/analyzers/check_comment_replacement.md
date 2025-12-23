---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: hook
---

# Check Comment Replacement

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///

"""
Detect when code is replaced with comments.

This hook prevents replacing functional code with comments.
Runs after Edit or MultiEdit operations.
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from hook_logging import hook_invocation


def is_comment(line: str) -> bool:
    stripped = line.strip()
    comment_patterns = [
        r"^\s*//",
        r"^\s*#",
        r"^\s*/\*",
        r"^\s*\*",
        r"^\s*\*/",
        r"^\s*<!--",
        r"^\s*-->",
    ]
    return any(re.match(pattern, stripped) for pattern in comment_patterns)


def is_comment_replacement(old_string: str, new_string: str) -> bool:
    old_lines = old_string.strip().split("\n")
    new_lines = new_string.strip().split("\n")

    old_code_lines = [
        line for line in old_lines if line.strip() and not is_comment(line)
    ]
    new_code_lines = [
        line for line in new_lines if line.strip() and not is_comment(line)
    ]

    old_comment_lines = [line for line in old_lines if is_comment(line)]
    new_comment_lines = [line for line in new_lines if is_comment(line)]

    if (
        len(old_code_lines) >= 3
        and len(new_code_lines) == 0
        and len(new_comment_lines) > 0
    ):
        return True

    return (
        len(old_code_lines) >= 3
        and len(new_code_lines) <= 1
        and len(new_comment_lines) >= len(old_comment_lines) + 2
    )


def main() -> None:
    with hook_invocation("check_comment_replacement") as inv:
        try:
            payload = json.load(sys.stdin)
        except json.JSONDecodeError:
            sys.exit(0)

        inv.set_payload(payload)

        if payload.get("stop_hook_active"):
            sys.exit(0)

        tool_name = payload.get("tool_name")
        if tool_name not in ["Edit", "MultiEdit"]:
            sys.exit(0)

        tool_input = payload.get("tool_input", {})
        if not tool_input or not isinstance(tool_input, dict):
            sys.exit(0)

        old_string = tool_input.get("old_string", "")
        new_string = tool_input.get("new_string", "")

        if not old_string or not new_string:
            sys.exit(0)

        if is_comment_replacement(old_string, new_string):
            print("[Error] Code replaced with comments", file=sys.stderr)
            print(
                "  Details: Detected replacement of functional code with comments",
                file=sys.stderr,
            )
            print("  Hints:", file=sys.stderr)
            print(
                "    - Implement the actual functionality instead of commenting",
                file=sys.stderr,
            )
            print(
                "    - If removing code, delete it entirely rather than commenting out",
                file=sys.stderr,
            )
            print(
                "    - Use TODO comments only when planning future work",
                file=sys.stderr,
            )
            sys.exit(1)

        sys.exit(0)


if __name__ == "__main__":
    main()
```
