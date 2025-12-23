#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Branch protection hook.

Blocks direct commits and pushes to protected branches (main, master, production).
Runs on PreToolUse for Bash commands.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent.parent))
from hook_logging import hook_invocation


PROTECTED_BRANCHES = {"main", "master", "production", "prod", "release"}

# Patterns that indicate commits/pushes to protected branches
DANGEROUS_PATTERNS = [
    # git push to protected branch
    (r"git\s+push\s+(?:origin\s+)?({branches})\b", "Push to protected branch"),
    # git push with -f/--force to protected branch
    (r"git\s+push\s+.*(?:-f|--force).*\s+({branches})\b", "Force push to protected branch"),
    # git commit on protected branch (when combined with push)
    (r"git\s+push\s+.*({branches})\b", "Push to protected branch"),
    # Direct checkout and commit pattern
    (r"git\s+checkout\s+({branches})\s*&&\s*git\s+commit", "Commit on protected branch"),
]


def check_command(command: str) -> str | None:
    """Check if command targets a protected branch."""
    branches_pattern = "|".join(re.escape(b) for b in PROTECTED_BRANCHES)

    for pattern_template, description in DANGEROUS_PATTERNS:
        pattern = pattern_template.format(branches=branches_pattern)
        if re.search(pattern, command, re.IGNORECASE):
            # Extract which branch
            match = re.search(branches_pattern, command, re.IGNORECASE)
            branch = match.group(0) if match else "protected"
            return f"{description}: '{branch}'"

    return None


def main() -> None:
    with hook_invocation("branch_protection") as inv:
        try:
            payload = json.load(sys.stdin)
        except json.JSONDecodeError:
            sys.exit(0)

        inv.set_payload(payload)

        if payload.get("stop_hook_active"):
            sys.exit(0)

        tool_name = payload.get("tool_name")
        if tool_name != "Bash":
            sys.exit(0)

        tool_input = payload.get("tool_input", {})
        command = tool_input.get("command", "") if isinstance(tool_input, dict) else ""

        if not command:
            sys.exit(0)

        if danger := check_command(command):
            print(f"[Error] Branch protection: {danger}", file=sys.stderr)
            print("\nHint: Create a feature branch instead:", file=sys.stderr)
            print("  git checkout -b feature/your-feature", file=sys.stderr)
            print("  git push origin feature/your-feature", file=sys.stderr)
            sys.exit(2)

        sys.exit(0)


if __name__ == "__main__":
    main()
