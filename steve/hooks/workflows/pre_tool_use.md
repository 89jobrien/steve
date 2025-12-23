---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: hook
---

# Pre Tool Use

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml"]
# ///
"""
PreToolUse workflow - runs all guard checks before tool execution.

This workflow imports and runs individual guard modules in sequence.
If any guard blocks (returns 2), the workflow blocks.
If any guard warns (returns 1), warnings are collected and shown.
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

# Add hooks root to path
HOOKS_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(HOOKS_ROOT))

from hook_logging import hook_invocation  # noqa: E402


@dataclass
class CheckResult:
    """Result of a guard check."""

    name: str
    passed: bool
    block: bool = False
    message: str | None = None
    hints: list[str] | None = None


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
    """Check if a guard is enabled in config."""
    guards_config = config.get("guards", {})
    check_config = guards_config.get(check_name, {})
    # Default to enabled if not specified
    if isinstance(check_config, dict):
        return check_config.get("enabled", True)
    return True


def run_guards(payload: dict[str, Any], config: dict) -> list[CheckResult]:
    """Run all guard checks and collect results."""
    results: list[CheckResult] = []
    tool_name = payload.get("tool_name", "")
    tool_input = payload.get("tool_input", {})
    cwd = payload.get("cwd", ".")

    # Bash tool checks
    if tool_name == "Bash":
        command = tool_input.get("command", "") if isinstance(tool_input, dict) else ""

        # Dangerous command check
        if is_enabled("dangerous_commands", config) and command:
            from guards.dangerous_command_guard import check_command

            is_dangerous, reason = check_command(command)
            if is_dangerous:
                results.append(
                    CheckResult(
                        name="dangerous_command",
                        passed=False,
                        block=True,
                        message=f"Blocked dangerous command: {reason}",
                        hints=[
                            "Review the command carefully before execution",
                            "Consider safer alternatives",
                            "If intentional, run manually in terminal",
                        ],
                    )
                )

        # Branch protection check
        if is_enabled("branch_protection", config) and command:
            from guards.branch_protection import check_command as check_branch

            danger = check_branch(command)
            if danger:
                results.append(
                    CheckResult(
                        name="branch_protection",
                        passed=False,
                        block=True,
                        message=f"Branch protection: {danger}",
                        hints=[
                            "Create a feature branch instead",
                            "Use pull request workflow",
                        ],
                    )
                )

    # Write/Edit tool checks
    if tool_name in ("Write", "Edit", "MultiEdit"):
        file_path = (
            tool_input.get("file_path", "") if isinstance(tool_input, dict) else ""
        )
        content = tool_input.get("content", "") if isinstance(tool_input, dict) else ""
        new_string = (
            tool_input.get("new_string", "") if isinstance(tool_input, dict) else ""
        )
        check_content = content or new_string

        # Secret scanner
        if is_enabled("secrets", config) and check_content:
            from guards.secret_scanner import scan_for_secrets

            secrets_found = scan_for_secrets(check_content)
            if secrets_found:
                secret_types = [s[1] for s in secrets_found[:3]]  # First 3 types
                results.append(
                    CheckResult(
                        name="secret_scanner",
                        passed=False,
                        block=True,
                        message=f"Found potential secrets: {', '.join(secret_types)}",
                        hints=[
                            "Use environment variables instead",
                            "Add to .env file (excluded from git)",
                            "Use a secrets manager",
                        ],
                    )
                )

        # File protection
        if is_enabled("file_protection", config) and file_path:
            from guards.file_protection import is_protected_file

            is_protected, reason = is_protected_file(file_path)
            if is_protected:
                results.append(
                    CheckResult(
                        name="file_protection",
                        passed=False,
                        block=True,
                        message=f"Protected file: {reason}",
                        hints=["This file is protected from modification"],
                    )
                )

        # Large file guard
        if is_enabled("large_file", config) and check_content:
            from guards.large_file_guard import (
                BLOCK_THRESHOLD,
                WARN_THRESHOLD,
                format_size,
                is_allowed_file,
            )

            if not is_allowed_file(file_path):
                content_size = len(check_content.encode("utf-8"))
                if content_size >= BLOCK_THRESHOLD:
                    results.append(
                        CheckResult(
                            name="large_file_guard",
                            passed=False,
                            block=True,
                            message=f"File too large: {format_size(content_size)} (limit: {format_size(BLOCK_THRESHOLD)})",
                            hints=["Consider splitting into smaller files"],
                        )
                    )
                elif content_size >= WARN_THRESHOLD:
                    results.append(
                        CheckResult(
                            name="large_file_guard",
                            passed=False,
                            block=False,
                            message=f"Large file warning: {format_size(content_size)}",
                        )
                    )

        # Path validation
        if is_enabled("path_validation", config) and file_path:
            from guards.path_validation import is_path_allowed

            is_valid, reason = is_path_allowed(file_path, cwd)
            if not is_valid:
                results.append(
                    CheckResult(
                        name="path_validation",
                        passed=False,
                        block=True,
                        message=f"Invalid path: {reason}",
                        hints=["Only write to project directories"],
                    )
                )

        # Readonly guard
        if is_enabled("readonly", config) and file_path:
            from guards.readonly_guard import is_readonly

            readonly, reason = is_readonly(file_path)
            if readonly:
                results.append(
                    CheckResult(
                        name="readonly_guard",
                        passed=False,
                        block=True,
                        message=f"Readonly file: {reason}",
                        hints=["This file should not be manually edited"],
                    )
                )

    return results


def build_json_output(
    decision: str | None = None,
    reason: str | None = None,
    system_message: str | None = None,
) -> dict[str, Any]:
    """Build proper JSON output per Claude Code hooks spec."""
    output: dict[str, Any] = {}

    if decision:
        output["hookSpecificOutput"] = {
            "hookEventName": "PreToolUse",
            "permissionDecision": decision,
        }
        if reason:
            output["hookSpecificOutput"]["permissionDecisionReason"] = reason

    if system_message:
        output["systemMessage"] = system_message

    return output


def main() -> None:
    with hook_invocation("pre_tool_use_workflow") as inv:
        try:
            payload = json.load(sys.stdin)
        except json.JSONDecodeError:
            sys.exit(0)

        inv.set_payload(payload)

        # Skip if stop hook is active (prevent recursion)
        if payload.get("stop_hook_active"):
            sys.exit(0)

        config = load_config()
        results = run_guards(payload, config)

        # Check for blocking results
        blocking = [r for r in results if r.block]
        warnings = [r for r in results if not r.block and not r.passed]

        if blocking:
            # Build denial reason from all blocking results
            reasons = []
            for result in blocking:
                msg = result.message or "Blocked"
                if result.hints:
                    msg += f" (Hints: {'; '.join(result.hints)})"
                reasons.append(msg)

            # Use JSON output with permissionDecision: deny
            output = build_json_output(
                decision="deny",
                reason=" | ".join(reasons),
            )
            print(json.dumps(output))
            # Log to stderr for visibility
            for result in blocking:
                print(f"[BLOCKED] {result.message}", file=sys.stderr)
            sys.exit(0)

        if warnings:
            # Warnings don't block, just show system message
            warning_msgs = [r.message for r in warnings if r.message]
            output = build_json_output(
                system_message=f"Warnings: {'; '.join(warning_msgs)}"
            )
            print(json.dumps(output))
            for result in warnings:
                print(f"[Warning] {result.message}", file=sys.stderr)
            sys.exit(0)

        # All checks passed
        sys.exit(0)


if __name__ == "__main__":
    main()
```
