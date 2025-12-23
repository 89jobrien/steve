---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: hook
---

# Complexity Checker

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Complexity checker hook.

Warns when functions exceed cyclomatic complexity threshold.
Runs on PostToolUse for Write/Edit operations on Python/TypeScript files.
"""

from __future__ import annotations

import asyncio
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from hook_logging import hook_invocation

# Complexity thresholds
WARN_THRESHOLD = 10
ERROR_THRESHOLD = 15

# Supported file extensions
SUPPORTED_EXTENSIONS = {".py", ".ts", ".tsx", ".js", ".jsx"}


def command_exists(cmd: str) -> bool:
    """Check if command exists on PATH."""
    return shutil.which(cmd) is not None


async def check_python_complexity(file_path: Path, cwd: str) -> list[str]:
    """Check Python file complexity using radon."""
    if not command_exists("radon"):
        return []

    try:
        proc = await asyncio.create_subprocess_exec(
            "radon",
            "cc",
            "-s",
            "-a",
            str(file_path),
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=30)
        output = stdout.decode()

        warnings = []
        for line in output.splitlines():
            # radon output format: "    F 10:0 function_name - C (12)"
            if " - " in line and "(" in line:
                try:
                    parts = line.rsplit("(", 1)
                    if len(parts) == 2:
                        complexity = int(parts[1].rstrip(")"))
                        func_part = parts[0].strip()
                        if complexity >= ERROR_THRESHOLD:
                            warnings.append(f"[Error] High complexity ({complexity}): {func_part}")
                        elif complexity >= WARN_THRESHOLD:
                            warnings.append(f"[Warning] Complexity ({complexity}): {func_part}")
                except (ValueError, IndexError):
                    continue

        return warnings
    except (asyncio.TimeoutError, OSError):
        return []


async def check_typescript_complexity(file_path: Path, cwd: str) -> list[str]:
    """Check TypeScript/JavaScript complexity using eslint complexity rule."""
    if not command_exists("eslint"):
        return []

    try:
        # Use eslint with complexity rule
        proc = await asyncio.create_subprocess_exec(
            "eslint",
            "--no-eslintrc",
            "--rule",
            f"complexity: [warn, {WARN_THRESHOLD}]",
            "--format",
            "compact",
            str(file_path),
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=30)
        output = stdout.decode()

        warnings = []
        for line in output.splitlines():
            if "complexity" in line.lower():
                warnings.append(f"[Warning] {line.strip()}")

        return warnings
    except (asyncio.TimeoutError, OSError):
        return []


async def check_complexity(file_path: Path, cwd: str) -> list[str]:
    """Check file complexity based on extension."""
    ext = file_path.suffix.lower()

    if ext == ".py":
        return await check_python_complexity(file_path, cwd)
    elif ext in {".ts", ".tsx", ".js", ".jsx"}:
        return await check_typescript_complexity(file_path, cwd)

    return []


def main() -> None:
    with hook_invocation("complexity_checker") as inv:
        try:
            payload = json.load(sys.stdin)
        except json.JSONDecodeError:
            sys.exit(0)

        inv.set_payload(payload)

        if payload.get("stop_hook_active"):
            sys.exit(0)

        tool_name = payload.get("tool_name")
        if tool_name not in ("Write", "Edit", "MultiEdit"):
            sys.exit(0)

        tool_input = payload.get("tool_input", {})
        if not isinstance(tool_input, dict):
            sys.exit(0)

        file_path = tool_input.get("file_path", "")
        cwd = payload.get("cwd", ".")

        if not file_path:
            sys.exit(0)

        path = Path(file_path)
        if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
            sys.exit(0)

        if not path.exists():
            sys.exit(0)

        warnings = asyncio.run(check_complexity(path, cwd))

        for warning in warnings:
            print(warning, file=sys.stderr)

        if warnings:
            print("\nHint: Consider refactoring complex functions:", file=sys.stderr)
            print("  - Extract helper functions", file=sys.stderr)
            print("  - Use early returns to reduce nesting", file=sys.stderr)
            print("  - Apply strategy pattern for conditionals", file=sys.stderr)

        sys.exit(0)


if __name__ == "__main__":
    main()
```
