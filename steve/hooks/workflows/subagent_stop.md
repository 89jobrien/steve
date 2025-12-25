---
name: subagent-stop
description: SubagentStop workflow - runs when a Claude Code subagent (Task tool) finishes.
author: Joseph OBrien
status: unpublished
updated: 2025-12-23
version: 1.0.1
tag: hook
---
# Subagent Stop

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml"]
# ///
"""
SubagentStop workflow - runs when a Claude Code subagent (Task tool) finishes.

Useful for:
- Evaluating if subagent completed its task
- Deciding if additional work is needed
- Providing feedback to continue or stop
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


def build_json_output(
    decision: str | None = None,
    reason: str | None = None,
) -> dict:
    """Build proper JSON output per Claude Code hooks spec.

    For SubagentStop hooks:
    - decision: "block" prevents subagent from stopping, reason tells it how to proceed
    - decision: undefined allows subagent to stop
    """
    output: dict = {}

    if decision:
        output["decision"] = decision
        if reason:
            output["reason"] = reason

    return output


def main() -> None:
    with hook_invocation("subagent_stop_workflow") as inv:
        try:
            payload = json.load(sys.stdin)
        except json.JSONDecodeError:
            sys.exit(0)

        inv.set_payload(payload)

        # IMPORTANT: Check stop_hook_active to prevent infinite loops
        if payload.get("stop_hook_active"):
            sys.exit(0)

        # Load config (could add subagent-specific rules)
        load_config()

        # By default, allow subagent to stop
        # To make subagent continue, uncomment:
        # output = build_json_output(
        #     decision="block",
        #     reason="Please verify the implementation before stopping"
        # )
        # print(json.dumps(output))

        sys.exit(0)


if __name__ == "__main__":
    main()
```
