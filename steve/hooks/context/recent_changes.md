---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: hook
---

# Recent Changes

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Recent changes hook.

Injects recent git changes as context when relevant keywords are detected.
Runs on UserPromptSubmit.
"""

from __future__ import annotations

import asyncio
import json
import re
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from hook_logging import hook_invocation

# Keywords that suggest user wants to know about recent changes
TRIGGER_KEYWORDS = [
    r"\brecent(ly)?\b",
    r"\blast\s+(commit|change|update|modification)",
    r"\bwhat\s+(did|have)\s+(i|we|you)\s+(change|modify|update)",
    r"\bwhat'?s?\s+(new|changed|different)",
    r"\bhistory\b",
    r"\bchangelog\b",
    r"\bdiff\b",
    r"\bgit\s+log\b",
    r"\bcommit\s+(history|message)",
]


def should_inject(prompt: str) -> bool:
    """Check if prompt suggests need for recent changes context."""
    prompt_lower = prompt.lower()
    return any(re.search(p, prompt_lower) for p in TRIGGER_KEYWORDS)


async def get_recent_changes(cwd: str, limit: int = 5) -> str:
    """Get recent git changes."""
    if not shutil.which("git"):
        return ""

    try:
        # Check if in git repo
        proc = await asyncio.create_subprocess_exec(
            "git",
            "rev-parse",
            "--git-dir",
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        await asyncio.wait_for(proc.communicate(), timeout=5)
        if proc.returncode != 0:
            return ""

        # Get recent commits
        proc = await asyncio.create_subprocess_exec(
            "git",
            "log",
            "--oneline",
            "--no-decorate",
            f"-{limit}",
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=10)
        commits = stdout.decode().strip()

        # Get changed files (unstaged)
        proc = await asyncio.create_subprocess_exec(
            "git",
            "status",
            "--short",
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=10)
        status = stdout.decode().strip()

        # Get diff stat for last commit
        proc = await asyncio.create_subprocess_exec(
            "git",
            "diff",
            "--stat",
            "HEAD~1",
            "--",
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=10)
        diff_stat = stdout.decode().strip()

        output_parts = []

        if commits:
            output_parts.append(f"**Recent Commits:**\n```\n{commits}\n```")

        if status:
            output_parts.append(f"**Uncommitted Changes:**\n```\n{status}\n```")

        if diff_stat and len(diff_stat) < 500:
            output_parts.append(f"**Last Commit Stats:**\n```\n{diff_stat}\n```")

        return "\n\n".join(output_parts)

    except (asyncio.TimeoutError, OSError):
        return ""


def main() -> None:
    with hook_invocation("recent_changes") as inv:
        try:
            payload = json.load(sys.stdin)
        except json.JSONDecodeError:
            sys.exit(0)

        inv.set_payload(payload)

        if payload.get("stop_hook_active"):
            sys.exit(0)

        prompt = payload.get("prompt", "")
        cwd = payload.get("cwd", ".")

        if not prompt:
            sys.exit(0)

        if not should_inject(prompt):
            sys.exit(0)

        changes = asyncio.run(get_recent_changes(cwd))

        if changes:
            # Output to stdout for context injection
            print(f"\n---\n**Recent Changes Context:**\n{changes}\n---\n")
            print("[Success] Injected recent git changes context", file=sys.stderr)

        sys.exit(0)


if __name__ == "__main__":
    main()
```
