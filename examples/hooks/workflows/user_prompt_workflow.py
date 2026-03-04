#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml"]
# ///
"""UserPromptSubmit workflow - orchestrates context injection when user submits prompt.

ARCHITECTURE: Thin orchestrator that composes context providers from context/ directory.

Orchestrates:
  - context/project_detector.py - Detects project type and injects framework hints
  - context/recent_changes.py - Injects recent git changes when relevant
  - context/related_files.py - Finds and suggests related files
  - context/jit_context.py - Just-in-time context injection

Exit codes:
  0 = Success (context injected to stdout for Claude to read)

This workflow should remain < 150 lines. Complex logic belongs in context/.
"""

from __future__ import annotations

import asyncio
import json
import sys
from pathlib import Path
from typing import Any

# Add hooks root to path
HOOKS_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(HOOKS_ROOT))

from context.project_detector import detect_project  # noqa: E402
from context.recent_changes import get_recent_changes, should_inject  # noqa: E402
from context.related_files import find_matching_files  # noqa: E402
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
    """Check if a context provider is enabled."""
    context_config = config.get("context", {})
    check_config = context_config.get(check_name, {})
    if isinstance(check_config, dict):
        return check_config.get("enabled", True)
    return True


def run_context_providers(payload: dict[str, Any], config: dict) -> list[str]:
    """Run context providers by composing imported hooks."""
    context_parts: list[str] = []
    cwd = payload.get("cwd", ".")
    prompt = payload.get("prompt", "")

    # Project detection - compose from context/project_detector.py
    if is_enabled("project_detector", config):
        detection = detect_project(cwd)
        if detection:
            project_type, context_hint = detection
            context_parts.append(f"{project_type}: {context_hint}")

    # Recent changes - compose from context/recent_changes.py
    if is_enabled("recent_changes", config) and should_inject(prompt):
        changes = asyncio.run(get_recent_changes(cwd))
        if changes:
            context_parts.append(changes)

    # Related files - compose from context/related_files.py
    if is_enabled("related_files", config) and len(prompt) > 20:
        related_files = find_matching_files(cwd, prompt)
        if related_files:
            files_list = ", ".join(str(f.relative_to(cwd)) for f in related_files[:5])
            context_parts.append(f"Possibly related files: {files_list}")

    return context_parts


def build_json_output(
    additional_context: str | None = None,
    decision: str | None = None,
    reason: str | None = None,
) -> dict:
    """Build proper JSON output per Claude Code hooks spec."""
    output: dict = {}

    if decision:
        output["decision"] = decision
        if reason:
            output["reason"] = reason

    if additional_context:
        output["hookSpecificOutput"] = {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": additional_context,
        }

    return output


def main() -> None:
    with hook_invocation("user_prompt_workflow") as inv:
        try:
            payload = json.load(sys.stdin)
        except json.JSONDecodeError:
            sys.exit(0)

        inv.set_payload(payload)

        if payload.get("stop_hook_active"):
            sys.exit(0)

        config = load_config()
        context_parts = run_context_providers(payload, config)

        # Output context via JSON (proper format per docs)
        if context_parts:
            context = "**Relevant Context:**\n" + "\n".join(context_parts)
            output = build_json_output(additional_context=context)
            print(json.dumps(output))

        sys.exit(0)


if __name__ == "__main__":
    main()
