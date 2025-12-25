---
name: lint-project
description: Run linting on entire project.
author: Joseph OBrien
status: unpublished
updated: 2025-12-23
version: 1.0.1
tag: hook
---
# Lint Project

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///

"""Run linting on entire project.

This hook runs all configured linters on the entire project.
Runs on Stop and SubagentStop events.
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


def detect_linters(project_root: Path) -> list[str]:
    linters = []

    if (
        (project_root / "biome.json").exists()
        or (project_root / "biome.jsonc").exists()
    ) and command_exists("biome"):
        linters.append("biome")

    if (
        (project_root / ".eslintrc.js").exists()
        or (project_root / ".eslintrc.json").exists()
    ) and command_exists("eslint"):
        linters.append("eslint")

    if (
        (project_root / "ruff.toml").exists()
        or (project_root / "pyproject.toml").exists()
    ) and command_exists("ruff"):
        linters.append("ruff")

    return linters


async def run_linter(linter: str, cwd: str) -> tuple[int, str, str]:
    if linter == "biome":
        args = ["biome", "check", "."]
    elif linter == "eslint":
        args = ["eslint", "."]
    elif linter == "ruff":
        args = ["ruff", "check", ".", "--fix", "--exit-zero"]
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
            proc.communicate(), timeout=60
        )
        return (
            proc.returncode or 0,
            stdout_bytes.decode("utf-8", errors="replace"),
            stderr_bytes.decode("utf-8", errors="replace"),
        )
    except (FileNotFoundError, TimeoutError, OSError):
        return 1, "", "Command failed"


async def main_async(payload: dict) -> int:
    if payload.get("stop_hook_active"):
        return 0

    cwd = payload.get("cwd", ".")
    project_root = Path(cwd)

    linters = detect_linters(project_root)
    if not linters:
        return 0

    print(f"[Progress] Running linters: {', '.join(linters)}", file=sys.stderr)

    results = []
    for linter in linters:
        exit_code, stdout, stderr = await run_linter(linter, cwd)
        results.append((linter, exit_code, stdout, stderr))

    failed_linters = [
        (linter, code, out, err) for linter, code, out, err in results if code != 0
    ]

    if failed_linters:
        print("[Error] Linting failed", file=sys.stderr)
        print(
            f"  Details: {len(failed_linters)} linter(s) found issues", file=sys.stderr
        )
        print("  Hints:", file=sys.stderr)
        print("    - Fix linting issues before stopping", file=sys.stderr)
        print("    - Run linters locally with --fix flag", file=sys.stderr)

        for linter, code, stdout, stderr in failed_linters:
            print(f"\n{linter} (exit code {code}):", file=sys.stderr)
            if stdout:
                print(stdout, file=sys.stderr)
            if stderr:
                print(stderr, file=sys.stderr)

        return 1

    print("[Success] All linters passed", file=sys.stderr)
    return 0


def main() -> None:
    with hook_invocation("lint_project") as inv:
        try:
            payload = json.load(sys.stdin)
        except json.JSONDecodeError:
            sys.exit(0)

        inv.set_payload(payload)
        sys.exit(asyncio.run(main_async(payload)))


if __name__ == "__main__":
    main()
```
