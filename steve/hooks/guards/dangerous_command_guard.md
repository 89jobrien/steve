---
name: dangerous-command-guard
description: Block dangerous shell commands before execution.
author: Joseph OBrien
status: unpublished
updated: 2025-12-23
version: 1.0.1
tag: hook
---
# Dangerous Command Guard

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///

"""
Block dangerous shell commands before execution.

This hook blocks destructive commands like rm -rf, git push -f, DROP TABLE, etc.
Runs before Bash tool execution (PreToolUse).
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from hook_logging import hook_invocation

DANGEROUS_PATTERNS = [
    # Destructive file operations
    (
        r"\brm\s+(-[a-zA-Z]*r[a-zA-Z]*\s+|.*-[a-zA-Z]*f[a-zA-Z]*\s+).*(/|~|\$HOME|\*)",
        "Recursive/forced delete",
    ),
    (r"\brm\s+-rf\s+/", "Root filesystem deletion"),
    (r">\s*/dev/sd[a-z]", "Direct disk write"),
    (r"\bmkfs\b", "Filesystem format"),
    (r"\bdd\s+.*of=/dev/", "Direct disk overwrite"),
    # Git destructive operations
    (r"\bgit\s+push\s+.*--force\b", "Force push"),
    (r"\bgit\s+push\s+.*-f\b", "Force push"),
    (r"\bgit\s+reset\s+--hard", "Hard reset"),
    (r"\bgit\s+clean\s+-fd", "Force clean"),
    # Database destructive operations
    (r"\bDROP\s+(DATABASE|TABLE|SCHEMA)\b", "Database drop"),
    (r"\bTRUNCATE\s+TABLE\b", "Table truncate"),
    (r"\bDELETE\s+FROM\s+\w+\s*;?\s*$", "Delete without WHERE"),
    # System destructive operations
    (r"\bchmod\s+(-R\s+)?777\s+/", "Insecure permissions on root"),
    (r"\bchown\s+-R\s+.*\s+/\s*$", "Recursive chown on root"),
    (r":\(\)\s*\{\s*:\|:&\s*\}\s*;:", "Fork bomb"),
    # Credential/key operations
    (r"\bcurl\s+.*\|\s*(ba)?sh", "Piping curl to shell"),
    (r"\bwget\s+.*\|\s*(ba)?sh", "Piping wget to shell"),
    # Environment destruction
    (r"\bunset\s+(PATH|HOME|USER)", "Unsetting critical env vars"),
    (r"\bexport\s+PATH\s*=\s*$", "Clearing PATH"),
]


def check_command(command: str) -> tuple[bool, str | None]:
    """Check if command matches any dangerous pattern."""
    for pattern, description in DANGEROUS_PATTERNS:
        if re.search(pattern, command, re.IGNORECASE):
            return True, description
    return False, None


def main() -> None:
    with hook_invocation("dangerous_command_guard") as inv:
        try:
            payload = json.load(sys.stdin)
        except json.JSONDecodeError:
            sys.exit(0)

        inv.set_payload(payload)

        tool_input = payload.get("tool_input", {})
        command = tool_input.get("command") if isinstance(tool_input, dict) else None

        if not command:
            sys.exit(0)

        is_dangerous, reason = check_command(command)

        if is_dangerous:
            print(f"[Error] Blocked dangerous command: {reason}", file=sys.stderr)
            print(f"  Command: {command[:100]}...", file=sys.stderr)
            print("  Hints:", file=sys.stderr)
            print(
                "    - Review the command carefully before execution", file=sys.stderr
            )
            print("    - Consider safer alternatives", file=sys.stderr)
            print("    - If intentional, run manually in terminal", file=sys.stderr)
            sys.exit(2)

        sys.exit(0)


if __name__ == "__main__":
    main()
```
