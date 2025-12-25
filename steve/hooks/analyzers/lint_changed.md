---
name: lint-changed
description: Run linting on changed files.
author: Joseph OBrien
status: unpublished
updated: 2025-12-23
version: 1.0.1
tag: hook
---
# Lint Changed

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///

"""
Run linting on changed files.

This hook runs the appropriate linter (biome, eslint, ruff) on changed files.
Runs after Write, Edit, or MultiEdit operations.
"""

import asyncio
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from hook_logging import hook_invocation


def command_exists(cmd: str) -> bool:
    return shutil.which(cmd) is not None


def detect_linter(project_root: Path) -> str | None:
    if (
        (project_root / "biome.json").exists()
        or (project_root / "biome.jsonc").exists()
    ) and command_exists("biome"):
        return "biome"

    if (
        (project_root / ".eslintrc.js").exists()
        or (project_root / ".eslintrc.json").exists()
    ) and command_exists("eslint"):
        return "eslint"

    if (
        (project_root / "ruff.toml").exists()
        or (project_root / "pyproject.toml").exists()
    ) and command_exists("ruff"):
        return "ruff"

    return None


async def run_linter(linter: str, file_path: str, cwd: str) -> tuple[int, str, str]:
    args = []

    if linter == "biome":
        args = ["biome", "check", file_path]
    elif linter == "eslint":
        args = ["eslint", file_path]
    elif linter == "ruff":
        args = ["ruff", "check", "--fix", "--exit-zero", file_path]
    else:
        return 1, "", "Unknown linter"

    try:
        proc = await asyncio.create_subprocess_exec(
            *args,
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout_bytes, stderr_bytes = await asyncio.wait_for(
            proc.communicate(), timeout=30
        )
        return (
            proc.returncode or 0,
            stdout_bytes.decode("utf-8", errors="replace"),
            stderr_bytes.decode("utf-8", errors="replace"),
        )
    except (FileNotFoundError, TimeoutError, OSError):
        return 1, "", "Command failed"


def main() -> None:
    with hook_invocation("lint_changed") as inv:
        try:
            payload = json.load(sys.stdin)
        except json.JSONDecodeError:
            sys.exit(0)

        inv.set_payload(payload)

        if payload.get("stop_hook_active"):
            sys.exit(0)

        tool_input = payload.get("tool_input", {})
        file_path = (
            tool_input.get("file_path") if isinstance(tool_input, dict) else None
        )

        if not file_path:
            sys.exit(0)

        path = Path(file_path)
        if not path.exists():
            sys.exit(0)

        cwd = payload.get("cwd", ".")
        project_root = Path(cwd)

        linter = detect_linter(project_root)
        if not linter:
            sys.exit(0)

        print(f"[Progress] Running {linter} on {path.name}", file=sys.stderr)

        exit_code, stdout, stderr = asyncio.run(run_linter(linter, file_path, cwd))

        if exit_code != 0:
            print(f"[Error] {linter} found issues", file=sys.stderr)
            print(
                f"  Details: Linting failed with exit code {exit_code}", file=sys.stderr
            )
            print("  Hints:", file=sys.stderr)
            print(
                f"    - Run '{linter} --fix {path.name}' to auto-fix issues",
                file=sys.stderr,
            )
            print("    - Review the linter output above for details", file=sys.stderr)

            if stdout:
                print(stdout, file=sys.stderr)
            if stderr:
                print(stderr, file=sys.stderr)

            sys.exit(1)

        print(f"[Success] {linter} passed", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
```
