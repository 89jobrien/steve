#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///

"""Git auto-checkpoint on stop.

This hook creates automatic git stash checkpoints when stopping.
Runs on Stop and SubagentStop events.
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent.parent))
from hook_logging import hook_invocation


async def run_git_command(args: list[str], cwd: str, timeout: int = 30) -> tuple[int, str, str]:
    try:
        proc = await asyncio.create_subprocess_exec(
            "git",
            *args,
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout_bytes, stderr_bytes = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        return (
            proc.returncode or 0,
            stdout_bytes.decode("utf-8", errors="replace"),
            stderr_bytes.decode("utf-8", errors="replace"),
        )
    except (FileNotFoundError, TimeoutError, OSError):
        return 1, "", "Command failed"


async def cleanup_old_checkpoints(project_root: str, prefix: str, max_checkpoints: int) -> None:
    exit_code, stdout, _ = await run_git_command(["stash", "list"], project_root, timeout=10)

    if exit_code != 0:
        return

    checkpoints = []
    for line in stdout.split("\n"):
        if prefix in line:
            parts = line.split(":", 1)
            if len(parts) > 0:
                stash_id = parts[0].strip()
                checkpoints.append(stash_id)

    if len(checkpoints) > max_checkpoints:
        to_drop = checkpoints[max_checkpoints:]
        print(
            f"[Progress] Cleaning up {len(to_drop)} old checkpoint(s)...",
            file=sys.stderr,
        )

        for stash_id in to_drop:
            await run_git_command(["stash", "drop", stash_id], project_root, timeout=5)


async def main_async(payload: dict) -> int:
    if payload.get("stop_hook_active"):
        return 0

    prefix = "checkpoint"
    max_checkpoints = 10

    cwd = payload.get("cwd", ".")
    project_root = Path(cwd)
    git_dir = project_root / ".git"

    if not git_dir.exists():
        return 0

    exit_code, stdout, _ = await run_git_command(["status", "--porcelain"], cwd, timeout=5)

    if exit_code != 0 or not stdout.strip():
        return 0

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    stash_message = f"{prefix}_{timestamp}"

    print("[Progress] Creating checkpoint...", file=sys.stderr)

    exit_code, stdout, stderr = await run_git_command(
        ["stash", "push", "-u", "-m", stash_message], cwd, timeout=30
    )

    if exit_code == 0:
        print(f"[Success] Checkpoint created: {stash_message}", file=sys.stderr)

        await cleanup_old_checkpoints(cwd, prefix, max_checkpoints)
    else:
        print("[Error] Failed to create checkpoint", file=sys.stderr)
        print(f"  Details: {stderr}", file=sys.stderr)

    return exit_code


def main() -> None:
    with hook_invocation("create_checkpoint") as inv:
        try:
            payload = json.load(sys.stdin)
        except json.JSONDecodeError:
            sys.exit(0)

        inv.set_payload(payload)
        sys.exit(asyncio.run(main_async(payload)))


if __name__ == "__main__":
    main()
