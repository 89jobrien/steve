---
name: session-logger
description: Log all prompts for later review.
author: Joseph OBrien
status: unpublished
updated: 2025-12-23
version: 1.0.1
tag: hook
---
# Session Logger

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///

"""
Log all prompts for later review.

This hook logs prompts to a daily file for analysis.
Runs on UserPromptSubmit event.
"""

import json
import os
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from hook_logging import hook_invocation


def get_session_log_dir() -> Path:
    """Get the directory for session logs."""
    log_dir = Path.home() / ".claude" / "session-logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir


def get_session_log_path() -> Path:
    """Get the path for the current session log."""
    log_dir = get_session_log_dir()

    date_str = datetime.now().strftime("%Y%m%d")

    # Single file per day; include session_id in each record.
    return log_dir / f"prompts_{date_str}.jsonl"


def main() -> None:
    with hook_invocation("session_logger") as inv:
        try:
            payload = json.load(sys.stdin)
        except json.JSONDecodeError:
            return

        inv.set_payload(payload)

        prompt = payload.get("prompt", "")
        cwd = payload.get("cwd", "")

        if not prompt:
            return

        log_path = get_session_log_path()
        timestamp = datetime.now().isoformat()
        session_id = os.environ.get("CLAUDE_SESSION_ID", str(os.getpid()))

        log_entry = {
            "timestamp": timestamp,
            "session_id": session_id,
            "cwd": cwd,
            "prompt": prompt,
            "prompt_length": len(prompt),
        }

        try:
            with log_path.open("a") as f:
                f.write(json.dumps(log_entry) + "\n")
        except OSError:
            pass  # Silently fail - logging shouldn't break the session

        return


if __name__ == "__main__":
    main()
```
