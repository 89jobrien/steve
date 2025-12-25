---
name: session-end
description: SessionEnd workflow - runs when a Claude Code session ends.
author: Joseph OBrien
status: unpublished
updated: 2025-12-23
version: 1.0.1
tag: hook
---
# Session End

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml"]
# ///
"""
SessionEnd workflow - runs when a Claude Code session ends.

Useful for:
- Cleanup tasks
- Logging session statistics
- Saving session state

The 'reason' field indicates why the session ended:
- clear: Session cleared with /clear command
- logout: User logged out
- prompt_input_exit: User exited while prompt input was visible
- other: Other exit reasons
"""

from __future__ import annotations

import json
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
    """Check if a session end hook is enabled."""
    session_config = config.get("session", {})
    check_config = session_config.get(check_name, {})
    if isinstance(check_config, dict):
        return check_config.get("enabled", True)
    return True


def log_session_end(payload: dict[str, Any], config: dict) -> None:
    """Log session end to file."""
    session_config = config.get("session", {})
    log_dir = Path(session_config.get("log_dir", "~/.claude/logs")).expanduser()

    try:
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"session_{datetime.now():%Y%m%d}.jsonl"

        record = {
            "timestamp": datetime.now().isoformat(),
            "session_id": payload.get("session_id", "unknown"),
            "reason": payload.get("reason", "unknown"),
            "cwd": payload.get("cwd", ""),
        }

        with log_file.open("a") as f:
            f.write(json.dumps(record) + "\n")
    except Exception:
        pass


def main() -> None:
    with hook_invocation("session_end_workflow") as inv:
        try:
            payload = json.load(sys.stdin)
        except json.JSONDecodeError:
            sys.exit(0)

        inv.set_payload(payload)

        config = load_config()
        reason = payload.get("reason", "unknown")

        # Log session end
        if is_enabled("session_logging", config):
            log_session_end(payload, config)

        # Export conversation if transcript available
        transcript_path = payload.get("transcript_path")
        cwd = payload.get("cwd", ".")
        if transcript_path:
            export_dir = get_output_dir(config)
            exported = export_transcript(
                transcript_path, export_dir, event_type="session_end", cwd=cwd
            )
            if exported:
                print(f"[Conversation exported: {exported.name}]", file=sys.stderr)

        # Print summary to stderr
        print(f"[Session ended: {reason}]", file=sys.stderr)

        # SessionEnd hooks cannot block session termination
        sys.exit(0)


if __name__ == "__main__":
    main()
```
