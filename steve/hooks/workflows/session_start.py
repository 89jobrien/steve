#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml"]
# ///
"""SessionStart workflow - runs when a Claude Code session starts.

Useful for:
- Loading development context (issues, recent changes)
- Installing dependencies
- Setting up environment variables via CLAUDE_ENV_FILE
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


# Add hooks root to path
HOOKS_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(HOOKS_ROOT))

from hook_logging import hook_invocation  # noqa: E402


def load_config() -> dict[str, Any]:
    """Load hooks configuration."""
    config_path = HOOKS_ROOT / "hooks_config.yaml"
    if not config_path.exists():
        return {}
    try:
        import yaml

        with config_path.open() as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def is_enabled(check_name: str, config: dict) -> bool:
    """Check if a session start hook is enabled."""
    session_config = config.get("session", {})
    check_config = session_config.get(check_name, {})
    if isinstance(check_config, dict):
        return check_config.get("enabled", True)
    return True


def get_git_branch(cwd: str) -> str | None:
    """Get current git branch."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            check=False,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return None


def get_recent_commits(cwd: str, count: int = 3) -> list[str]:
    """Get recent commit messages."""
    try:
        result = subprocess.run(
            ["git", "log", f"-{count}", "--oneline"],
            check=False,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return result.stdout.strip().split("\n")
    except Exception:
        pass
    return []


def get_uncommitted_changes(cwd: str) -> str | None:
    """Get summary of uncommitted changes."""
    try:
        result = subprocess.run(
            ["git", "status", "--short"],
            check=False,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            lines = result.stdout.strip().split("\n")
            return f"{len(lines)} file(s) with uncommitted changes"
    except Exception:
        pass
    return None


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
    context_parts: list[str] = []
    cwd = payload.get("cwd", ".")
    source = payload.get("source", "startup")  # startup, resume, clear, compact

    # Git context
    if is_enabled("git_context", config):
        branch = get_git_branch(cwd)
        if branch:
            context_parts.append(f"Git branch: {branch}")

        commits = get_recent_commits(cwd)
        if commits:
            context_parts.append(f"Recent commits: {'; '.join(commits[:3])}")

        changes = get_uncommitted_changes(cwd)
        if changes:
            context_parts.append(f"Uncommitted: {changes}")

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
