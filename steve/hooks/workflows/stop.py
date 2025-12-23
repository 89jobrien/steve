#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml"]
# ///
"""Stop workflow - runs lifecycle hooks when session ends.

This workflow runs end-of-session tasks including:
- Session metrics collection
- Commit suggestions
- Knowledge updates
- Cleanup
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


# Add hooks root to path
HOOKS_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(HOOKS_ROOT))

from hook_logging import hook_invocation  # noqa: E402
from lifecycle.export_conversation import (  # noqa: E402
    export_transcript,
    get_output_dir,
)


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
    """Check if a lifecycle hook is enabled."""
    lifecycle_config = config.get("lifecycle", {})
    check_config = lifecycle_config.get(check_name, {})
    if isinstance(check_config, dict):
        return check_config.get("enabled", True)
    return True


def collect_metrics(transcript_path: str | None) -> dict[str, Any]:
    """Collect session metrics from transcript."""
    metrics = {
        "timestamp": datetime.now().isoformat(),
        "tools_used": {},
        "files_modified": 0,
        "commands_run": 0,
    }

    if not transcript_path:
        return metrics

    path = Path(transcript_path)
    if not path.exists():
        return metrics

    try:
        with path.open() as f:
            data = json.load(f)

        messages = data if isinstance(data, list) else data.get("messages", [])

        for msg in messages:
            if not isinstance(msg, dict):
                continue

            # Count tool uses
            content = msg.get("content", [])
            if isinstance(content, list):
                for item in content:
                    if isinstance(item, dict) and item.get("type") == "tool_use":
                        tool = item.get("name", "unknown")
                        metrics["tools_used"][tool] = metrics["tools_used"].get(tool, 0) + 1

                        if tool in ("Write", "Edit", "MultiEdit"):
                            metrics["files_modified"] += 1
                        elif tool == "Bash":
                            metrics["commands_run"] += 1

    except Exception:
        pass

    return metrics


def suggest_commit(cwd: str) -> str | None:
    """Generate commit message suggestion based on changes."""
    try:
        # Get staged and unstaged changes
        result = subprocess.run(
            ["git", "diff", "--stat", "HEAD"],
            check=False,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=5,
        )

        if result.returncode != 0 or not result.stdout.strip():
            return None

        # Get list of changed files
        files_result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            check=False,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=5,
        )

        if files_result.returncode != 0:
            return None

        changed_files = files_result.stdout.strip().split("\n")
        if not changed_files or not changed_files[0]:
            return None

        # Determine commit type based on files
        commit_type = "chore"
        if any("test" in f.lower() for f in changed_files):
            commit_type = "test"
        elif any(f.endswith(".md") for f in changed_files):
            commit_type = "docs"
        elif any("fix" in f.lower() for f in changed_files):
            commit_type = "fix"
        else:
            commit_type = "feat"

        # Generate message
        file_count = len(changed_files)
        primary_file = Path(changed_files[0]).name
        scope = Path(changed_files[0]).parent.name if "/" in changed_files[0] else None

        if scope and scope != ".":
            message = f"{commit_type}({scope}): update {primary_file}"
        else:
            message = f"{commit_type}: update {primary_file}"

        if file_count > 1:
            message += f" and {file_count - 1} other file(s)"

        return message

    except Exception:
        return None


def save_metrics(metrics: dict[str, Any], config: dict) -> None:
    """Save metrics to file."""
    lifecycle_config = config.get("lifecycle", {})
    metrics_config = lifecycle_config.get("metrics", {})
    output_dir = Path(metrics_config.get("output_dir", "~/.claude/logs")).expanduser()

    try:
        output_dir.mkdir(parents=True, exist_ok=True)
        date_str = datetime.now().strftime("%Y%m%d")
        output_file = output_dir / f"metrics_{date_str}.jsonl"

        with output_file.open("a") as f:
            f.write(json.dumps(metrics) + "\n")
    except Exception:
        pass


def run_lifecycle_hooks(payload: dict[str, Any], config: dict) -> list[str]:
    """Run lifecycle hooks and collect output."""
    output: list[str] = []
    cwd = payload.get("cwd", ".")
    transcript_path = payload.get("transcript_path")

    # Metrics collection
    if is_enabled("metrics", config):
        metrics = collect_metrics(transcript_path)
        if metrics.get("tools_used"):
            save_metrics(metrics, config)
            tool_summary = ", ".join(f"{k}:{v}" for k, v in list(metrics["tools_used"].items())[:5])
            output.append(f"Session metrics: {tool_summary}")

    # Commit suggestion
    if is_enabled("commit_suggester", config):
        suggestion = suggest_commit(cwd)
        if suggestion:
            output.append(f"Suggested commit: {suggestion}")

    # Export conversation
    if is_enabled("export_conversation", config) and transcript_path:
        export_dir = get_output_dir(config)
        exported = export_transcript(transcript_path, export_dir, event_type="stop", cwd=cwd)
        if exported:
            output.append(f"Conversation exported: {exported.name}")

    return output


def build_json_output(
    decision: str | None = None,
    reason: str | None = None,
) -> dict:
    """Build proper JSON output per Claude Code hooks spec.

    For Stop hooks:
    - decision: "block" prevents Claude from stopping, reason tells Claude how to proceed
    - decision: undefined allows Claude to stop
    """
    output: dict = {}

    if decision:
        output["decision"] = decision
        if reason:
            output["reason"] = reason

    return output


def main() -> None:
    with hook_invocation("stop_workflow") as inv:
        try:
            payload = json.load(sys.stdin)
        except json.JSONDecodeError:
            sys.exit(0)

        inv.set_payload(payload)

        # IMPORTANT: Check stop_hook_active to prevent infinite loops
        if payload.get("stop_hook_active"):
            sys.exit(0)

        config = load_config()
        output = run_lifecycle_hooks(payload, config)

        # Print output to stderr for visibility
        if output:
            print("[Session Summary]", file=sys.stderr)
            for line in output:
                print(f"  - {line}", file=sys.stderr)

        # Note: We don't block stopping by default.
        # To make Claude continue, use:
        # output = build_json_output(decision="block", reason="Please complete X before stopping")
        # print(json.dumps(output))

        sys.exit(0)


if __name__ == "__main__":
    main()
