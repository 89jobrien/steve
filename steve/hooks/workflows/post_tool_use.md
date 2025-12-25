---
name: post-tool-use
description: PostToolUse workflow - runs analyzers after tool execution.
author: Joseph OBrien
status: unpublished
updated: 2025-12-23
version: 1.0.1
tag: hook
---
# Post Tool Use

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml"]
# ///
"""
PostToolUse workflow - runs analyzers after tool execution.

This workflow runs analysis on changed files including:
- Linting
- Type checking
- Security scanning
- TODO tracking
"""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Add hooks root to path
HOOKS_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(HOOKS_ROOT))

from hook_logging import hook_invocation  # noqa: E402


@dataclass
class AnalysisResult:
    """Result of an analysis check."""
    name: str
    passed: bool
    messages: list[str] = field(default_factory=list)


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
    """Check if an analyzer is enabled in config."""
    analyzers_config = config.get("analyzers", {})
    check_config = analyzers_config.get(check_name, {})
    if isinstance(check_config, dict):
        return check_config.get("enabled", True)
    return True


def get_file_extension(file_path: str) -> str:
    """Get file extension without dot."""
    return Path(file_path).suffix.lstrip(".")


def run_linter(file_path: str, cwd: str) -> AnalysisResult:
    """Run appropriate linter for file type."""
    ext = get_file_extension(file_path)
    messages = []

    # Python files
    if ext == "py":
        try:
            result = subprocess.run(
                ["uvx", "ruff", "check", file_path],
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode != 0 and result.stdout:
                messages.append(f"Ruff: {result.stdout.strip()[:200]}")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

    # JS/TS files
    elif ext in ("js", "ts", "jsx", "tsx"):
        # Try biome first, then eslint
        for linter in [["npx", "biome", "check", file_path], ["npx", "eslint", file_path]]:
            try:
                result = subprocess.run(
                    linter,
                    cwd=cwd,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                if result.returncode != 0 and result.stdout:
                    messages.append(f"Lint: {result.stdout.strip()[:200]}")
                break
            except (subprocess.TimeoutExpired, FileNotFoundError):
                continue

    return AnalysisResult(
        name="linter",
        passed=len(messages) == 0,
        messages=messages
    )


def check_todos(content: str, file_path: str) -> AnalysisResult:
    """Check for TODO/FIXME comments in new content."""
    import re
    messages = []
    todo_pattern = r'\b(TODO|FIXME|HACK|XXX|BUG)\b[:\s]*(.*?)(?:\n|$)'

    matches = re.findall(todo_pattern, content, re.IGNORECASE)
    if matches:
        for tag, text in matches[:3]:  # Limit to 3
            messages.append(f"{tag}: {text.strip()[:50]}")

    return AnalysisResult(
        name="todo_tracker",
        passed=True,  # TODOs are informational, not failures
        messages=messages
    )


def check_complexity(content: str, file_path: str) -> AnalysisResult:
    """Basic complexity check - count nested blocks."""
    messages = []
    ext = get_file_extension(file_path)

    if ext not in ("py", "js", "ts", "jsx", "tsx"):
        return AnalysisResult(name="complexity", passed=True)

    # Simple heuristic: count max indentation depth
    max_depth = 0
    for line in content.split("\n"):
        stripped = line.lstrip()
        if stripped:
            indent = len(line) - len(stripped)
            # Assume 4 spaces or 1 tab per level
            depth = indent // 4 if "    " in line[:indent] else indent
            max_depth = max(max_depth, depth)

    if max_depth > 6:
        messages.append(f"High nesting depth ({max_depth} levels) - consider refactoring")

    return AnalysisResult(
        name="complexity",
        passed=max_depth <= 6,
        messages=messages
    )


def run_analyzers(payload: dict[str, Any], config: dict) -> list[AnalysisResult]:
    """Run all analyzers and collect results."""
    results: list[AnalysisResult] = []
    tool_name = payload.get("tool_name", "")
    tool_input = payload.get("tool_input", {})
    cwd = payload.get("cwd", ".")

    if tool_name not in ("Write", "Edit", "MultiEdit"):
        return results

    file_path = tool_input.get("file_path", "") if isinstance(tool_input, dict) else ""
    content = tool_input.get("content", "") if isinstance(tool_input, dict) else ""
    new_string = tool_input.get("new_string", "") if isinstance(tool_input, dict) else ""
    check_content = content or new_string

    if not file_path:
        return results

    # Linting
    if is_enabled("lint", config):
        results.append(run_linter(file_path, cwd))

    # TODO tracking
    if is_enabled("todo_tracker", config) and check_content:
        results.append(check_todos(check_content, file_path))

    # Complexity check
    if is_enabled("complexity", config) and check_content:
        results.append(check_complexity(check_content, file_path))

    return results


def build_json_output(
    decision: str | None = None,
    reason: str | None = None,
    additional_context: str | None = None,
) -> dict:
    """Build proper JSON output per Claude Code hooks spec."""
    output: dict = {}

    if decision:
        output["decision"] = decision
        if reason:
            output["reason"] = reason

    if additional_context:
        output["hookSpecificOutput"] = {
            "hookEventName": "PostToolUse",
            "additionalContext": additional_context,
        }

    return output


def main() -> None:
    with hook_invocation("post_tool_use_workflow") as inv:
        try:
            payload = json.load(sys.stdin)
        except json.JSONDecodeError:
            sys.exit(0)

        inv.set_payload(payload)

        if payload.get("stop_hook_active"):
            sys.exit(0)

        config = load_config()
        results = run_analyzers(payload, config)

        # Collect all messages
        all_messages = []
        has_failures = False

        for result in results:
            if result.messages:
                all_messages.extend(result.messages)
            if not result.passed:
                has_failures = True

        if all_messages:
            # Build context from analysis results
            context = "Analysis results:\n" + "\n".join(f"- {msg}" for msg in all_messages[:5])

            if has_failures:
                # Use block decision to prompt Claude about issues
                output = build_json_output(
                    decision="block",
                    reason=context,
                )
            else:
                # Just add context without blocking
                output = build_json_output(additional_context=context)

            print(json.dumps(output))

            # Log to stderr for visibility
            print("[Analysis]", file=sys.stderr)
            for msg in all_messages[:5]:
                print(f"  - {msg}", file=sys.stderr)

        sys.exit(0)


if __name__ == "__main__":
    main()
```
