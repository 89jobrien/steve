---
name: git-diff-logger
description: Log git diffs for all file changes in a session.
author: Joseph OBrien
status: unpublished
updated: 2025-12-23
version: 1.0.1
tag: hook
---
# Git Diff Logger

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///

"""
Log git diffs for all file changes in a session.

This hook logs file changes to a session-specific diff file.
Runs after Write, Edit, or MultiEdit operations (PostToolUse).
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from hook_logging import hook_invocation


async def run_git_command(
    args: list[str], cwd: str, timeout: int = 10
) -> tuple[int, str, str]:
    try:
        proc = await asyncio.create_subprocess_exec(
            "git",
            *args,
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout_bytes, stderr_bytes = await asyncio.wait_for(
            proc.communicate(), timeout=timeout
        )
        return (
            proc.returncode or 0,
            stdout_bytes.decode("utf-8", errors="replace"),
            stderr_bytes.decode("utf-8", errors="replace"),
        )
    except (FileNotFoundError, TimeoutError, OSError):
        return 1, "", ""


async def get_file_diff(file_path: str, cwd: str) -> str | None:
    """Get diff for a specific file."""
    # Try staged diff first
    exit_code, stdout, _ = await run_git_command(
        ["diff", "--cached", "--", file_path], cwd
    )

    if exit_code == 0 and stdout.strip():
        return stdout

    # Try unstaged diff
    exit_code, stdout, _ = await run_git_command(["diff", "--", file_path], cwd)

    if exit_code == 0 and stdout.strip():
        return stdout

    # File might be new/untracked - show full content
    exit_code, stdout, _ = await run_git_command(
        ["diff", "--no-index", "/dev/null", file_path], cwd
    )

    if stdout.strip():
        return stdout

    return None


def get_session_log_path(cwd: str) -> Path:
    """Get the path for the session diff log."""
    # Use ~/.claude/session-diffs/ directory
    log_dir = Path.home() / ".claude" / "session-diffs"
    log_dir.mkdir(parents=True, exist_ok=True)

    # Create session-specific log file
    # Use date + PID for uniqueness
    session_id = os.environ.get("CLAUDE_SESSION_ID", str(os.getpid()))
    date_str = datetime.now().strftime("%Y%m%d")

    return log_dir / f"session_{date_str}_{session_id}.diff"


def main() -> None:
    with hook_invocation("git_diff_logger") as inv:
        try:
            payload = json.load(sys.stdin)
        except json.JSONDecodeError:
            sys.exit(0)

        inv.set_payload(payload)

        if payload.get("stop_hook_active"):
            sys.exit(0)

        tool_input = payload.get("tool_input", {})
        tool_name = payload.get("tool_name", "")
        file_path = (
            tool_input.get("file_path") if isinstance(tool_input, dict) else None
        )

        if not file_path:
            sys.exit(0)

        cwd = payload.get("cwd", ".")

        # Check if in a git repo
        git_dir = Path(cwd) / ".git"
        if not git_dir.exists():
            sys.exit(0)

        diff = asyncio.run(get_file_diff(file_path, cwd))

        if not diff:
            sys.exit(0)

        log_path = get_session_log_path(cwd)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Append to session log
        try:
            with log_path.open("a") as f:
                f.write(f"\n{'=' * 60}\n")
                f.write(f"# {tool_name}: {file_path}\n")
                f.write(f"# Time: {timestamp}\n")
                f.write(f"{'=' * 60}\n")
                f.write(diff)
                f.write("\n")

            print(f"[Progress] Logged diff to {log_path.name}", file=sys.stderr)
        except OSError as e:
            print(f"[Warning] Failed to log diff: {e}", file=sys.stderr)

        sys.exit(0)


if __name__ == "__main__":
    main()
```
