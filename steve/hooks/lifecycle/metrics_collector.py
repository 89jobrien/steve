#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Metrics collector hook.

Collects session metrics (files changed, operations, duration).
Runs on Stop event.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent.parent))
from hook_logging import hook_invocation


METRICS_DIR = Path.home() / ".claude" / "session-metrics"


def analyze_transcript(transcript_path: str) -> dict:
    """Analyze session transcript for metrics."""
    metrics = {
        "files_written": 0,
        "files_edited": 0,
        "files_read": 0,
        "bash_commands": 0,
        "web_fetches": 0,
        "agent_tasks": 0,
        "tools_used": {},
        "files_modified": set(),
        "unique_tools": set(),
    }

    path = Path(transcript_path)
    if not path.exists():
        return metrics

    try:
        content = path.read_text()
    except OSError:
        return metrics

    # Count tool usages
    tool_patterns = {
        "Write": '"tool_name": "Write"',
        "Edit": '"tool_name": "Edit"',
        "MultiEdit": '"tool_name": "MultiEdit"',
        "Read": '"tool_name": "Read"',
        "Bash": '"tool_name": "Bash"',
        "WebFetch": '"tool_name": "WebFetch"',
        "Task": '"tool_name": "Task"',
        "Glob": '"tool_name": "Glob"',
        "Grep": '"tool_name": "Grep"',
        "TodoWrite": '"tool_name": "TodoWrite"',
    }

    for tool, pattern in tool_patterns.items():
        count = content.count(pattern)
        if count > 0:
            metrics["tools_used"][tool] = count
            metrics["unique_tools"].add(tool)

    metrics["files_written"] = metrics["tools_used"].get("Write", 0)
    metrics["files_edited"] = metrics["tools_used"].get("Edit", 0) + metrics["tools_used"].get(
        "MultiEdit", 0
    )
    metrics["files_read"] = metrics["tools_used"].get("Read", 0)
    metrics["bash_commands"] = metrics["tools_used"].get("Bash", 0)
    metrics["web_fetches"] = metrics["tools_used"].get("WebFetch", 0)
    metrics["agent_tasks"] = metrics["tools_used"].get("Task", 0)

    # Extract file paths from transcript
    import re

    file_paths = re.findall(r'"file_path":\s*"([^"]+)"', content)
    metrics["files_modified"] = set(file_paths)

    # Convert sets to lists for JSON
    metrics["unique_tools"] = list(metrics["unique_tools"])
    metrics["files_modified"] = list(metrics["files_modified"])

    return metrics


def save_metrics(metrics: dict, cwd: str, session_id: str) -> Path:
    """Save metrics to file."""
    METRICS_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now()
    metrics_file = METRICS_DIR / f"metrics_{timestamp:%Y%m%d_%H%M%S}.json"

    record = {
        "timestamp": timestamp.isoformat(),
        "session_id": session_id,
        "cwd": cwd,
        **metrics,
        "summary": {
            "total_tool_calls": sum(metrics["tools_used"].values()),
            "total_files_touched": len(metrics["files_modified"]),
            "unique_tools_used": len(metrics["unique_tools"]),
        },
    }

    metrics_file.write_text(json.dumps(record, indent=2))
    return metrics_file


def format_summary(metrics: dict) -> str:
    """Format metrics as human-readable summary."""
    lines = [
        "Session Metrics:",
        f"  Files written:  {metrics['files_written']}",
        f"  Files edited:   {metrics['files_edited']}",
        f"  Files read:     {metrics['files_read']}",
        f"  Bash commands:  {metrics['bash_commands']}",
        f"  Agent tasks:    {metrics['agent_tasks']}",
        f"  Total files touched: {len(metrics['files_modified'])}",
        f"  Tools used: {', '.join(metrics['unique_tools'])}",
    ]
    return "\n".join(lines)


def main() -> None:
    with hook_invocation("metrics_collector") as inv:
        try:
            payload = json.load(sys.stdin)
        except json.JSONDecodeError:
            sys.exit(0)

        inv.set_payload(payload)

        transcript_path = payload.get("transcript_path", "")
        cwd = payload.get("cwd", ".")
        session_id = payload.get("session_id", "unknown")

        if not transcript_path:
            sys.exit(0)

        # Analyze transcript
        metrics = analyze_transcript(transcript_path)

        # Skip if no meaningful activity
        total_calls = sum(metrics["tools_used"].values())
        if total_calls < 3:
            sys.exit(0)

        # Save metrics
        metrics_file = save_metrics(metrics, cwd, session_id)

        # Output summary
        print("\n" + "=" * 50, file=sys.stderr)
        print(format_summary(metrics), file=sys.stderr)
        print(f"\n  Saved to: {metrics_file}", file=sys.stderr)
        print("=" * 50 + "\n", file=sys.stderr)

        sys.exit(0)


if __name__ == "__main__":
    main()
