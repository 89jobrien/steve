#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml"]
# ///
"""SessionStart workflow - orchestrates session initialization.

ARCHITECTURE: Thin orchestrator that composes utilities from lib/ directory.

Orchestrates:
  - lib/subprocess.py - Git commands for branch/commit/status info
  - lib/config.py - Configuration loading
  - context/codebase_map.py - Codebase structure visualization (called separately)

Outputs to stdout:
  - Git branch name
  - Recent commits (last 3)
  - Uncommitted changes count
  - Session resume source (clear/compact/startup)

This workflow should remain < 150 lines. Complex logic belongs in lib/.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

# Add hooks root to path
HOOKS_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(HOOKS_ROOT))

from hook_logging import hook_invocation  # noqa: E402
from lib.config import load_config  # noqa: E402


def is_enabled(check_name: str, config: dict) -> bool:
    """Check if a session start hook is enabled."""
    session_config = config.get("session", {})
    check_config = session_config.get(check_name, {})
    if isinstance(check_config, dict):
        return check_config.get("enabled", True)
    return True


def build_json_output(additional_context: str | None = None) -> dict:
    """Build proper JSON output per Claude Code hooks spec."""
    output: dict = {}

    if additional_context:
        output["hookSpecificOutput"] = {
            "hookEventName": "SessionStart",
            "additionalContext": additional_context,
        }

    return output


def run_session_start(payload: dict[str, Any], config: dict) -> list[str]:
    """Run session start hooks and collect context."""
    import asyncio  # noqa: E402, I001

    from lib.subprocess import (  # noqa: E402, I001
        get_git_branch,
        get_modified_files,
        git_command,
    )

    context_parts: list[str] = []
    cwd = payload.get("cwd", ".")
    source = payload.get("source", "startup")  # startup, resume, clear, compact

    # Git context
    if is_enabled("git_context", config):
        # Get current branch
        branch = asyncio.run(get_git_branch(cwd))
        if branch:
            context_parts.append(f"Git branch: {branch}")

        # Get recent commits
        result = asyncio.run(git_command(["log", "-3", "--oneline"], cwd=cwd))
        if result.success and result.stdout.strip():
            commits = result.stdout.strip().split("\n")
            context_parts.append(f"Recent commits: {'; '.join(commits[:3])}")

        # Get uncommitted changes
        modified = asyncio.run(get_modified_files(cwd))
        if modified:
            context_parts.append(f"Uncommitted: {len(modified)} file(s) with uncommitted changes")

    # Session source info
    if source != "startup":
        context_parts.append(f"Session resumed via: {source}")

    return context_parts


def main() -> None:
    with hook_invocation("session_start_workflow") as inv:
        try:
            payload = json.load(sys.stdin)
        except json.JSONDecodeError:
            sys.exit(0)

        inv.set_payload(payload)

        config = load_config()
        context_parts = run_session_start(payload, config)

        # Output context via JSON
        if context_parts:
            context = "**Session Context:**\n" + "\n".join(f"- {p}" for p in context_parts)
            output = build_json_output(additional_context=context)
            print(json.dumps(output))

        # Optional: Set environment variables via CLAUDE_ENV_FILE
        # Uncomment and modify to set env vars for the session:
        # env_file = os.environ.get("CLAUDE_ENV_FILE")
        # if env_file and is_enabled("env_setup", config):
        #     with open(env_file, "a") as f:
        #         f.write('export MY_VAR=value\n')

        sys.exit(0)


if __name__ == "__main__":
    main()
