#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml"]
# ///

"""Export conversation transcript to file.

This hook copies the raw conversation JSON to an export directory.
Runs on Stop and SessionEnd events.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


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


def is_enabled(config: dict) -> bool:
    """Check if export_conversation is enabled."""
    lifecycle_config = config.get("lifecycle", {})
    export_config = lifecycle_config.get("export_conversation", {})
    if isinstance(export_config, dict):
        return export_config.get("enabled", True)
    return True


def get_output_dir(config: dict) -> Path:
    """Get the output directory from config."""
    lifecycle_config = config.get("lifecycle", {})
    export_config = lifecycle_config.get("export_conversation", {})
    default_dir = "~/.claude/logs/exported_chatlogs"
    output_dir = (
        export_config.get("output_dir", default_dir)
        if isinstance(export_config, dict)
        else default_dir
    )
    return Path(output_dir).expanduser()


def cwd_to_path_slug(cwd: str) -> str:
    """Convert cwd to a filename-safe slug relative to home.

    Example: /Users/joe/dev/foo/bar -> __dev_foo_bar
             /Users/joe/.claude -> __claude
    """
    home = Path.home()
    cwd_path = Path(cwd)

    try:
        relative = cwd_path.relative_to(home)
        path_part = str(relative).replace("/", "_").replace(".", "_")
        # Strip leading underscores from dot-prefixed paths, then add __ separator
        path_part = path_part.lstrip("_")
        slug = "__" + path_part if path_part else "__root"
    except ValueError:
        # cwd is not under home, use full path
        slug = "__" + str(cwd_path).replace("/", "_").replace(".", "_").lstrip("_")

    return slug


def export_transcript(
    transcript_path: str,
    output_dir: Path,
    event_type: str = "stop",
    cwd: str = ".",
) -> Path | None:
    """Export the transcript to the output directory with metadata header.

    Args:
        transcript_path: Path to the source transcript JSON
        output_dir: Base directory for exports
        event_type: Event type for subdirectory ("stop" or "session_end")
        cwd: Current working directory for filename and metadata

    Returns:
        Path to the exported file, or None if export failed
    """
    source = Path(transcript_path)
    if not source.exists():
        return None

    # Create subdirectory based on event type
    event_dir = output_dir / event_type
    event_dir.mkdir(parents=True, exist_ok=True)

    # Build filename with cwd slug
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    session_id = os.environ.get("CLAUDE_SESSION_ID", str(os.getpid()))
    cwd_slug = cwd_to_path_slug(cwd)
    filename = f"conversation_{timestamp}{cwd_slug}.jsonl"
    dest = event_dir / filename

    # Build metadata header
    metadata = {
        "export_timestamp": datetime.now().isoformat(),
        "event_type": event_type,
        "cwd": cwd,
        "session_id": session_id,
        "source_transcript": transcript_path,
    }

    try:
        # Write metadata header + original content
        with dest.open("w") as f:
            f.write(json.dumps(metadata) + "\n")
            f.write(source.read_text())
        return dest
    except OSError:
        return None


def main() -> None:
    with hook_invocation("export_conversation") as inv:
        try:
            payload = json.load(sys.stdin)
        except json.JSONDecodeError:
            sys.exit(0)

        inv.set_payload(payload)

        if payload.get("stop_hook_active"):
            sys.exit(0)

        config = load_config()

        if not is_enabled(config):
            sys.exit(0)

        transcript_path = payload.get("transcript_path")
        if not transcript_path:
            sys.exit(0)

        output_dir = get_output_dir(config)
        cwd = payload.get("cwd", ".")
        exported_path = export_transcript(transcript_path, output_dir, cwd=cwd)

        if exported_path:
            print(
                f"[Success] Conversation exported to {exported_path.name}",
                file=sys.stderr,
            )
        else:
            print("[Warning] Failed to export conversation", file=sys.stderr)

        sys.exit(0)


if __name__ == "__main__":
    main()
