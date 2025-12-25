---
name: test-project
description: Run full test suite when stopping.
author: Joseph OBrien
status: unpublished
updated: 2025-12-23
version: 1.0.1
tag: hook
---
# Test Project

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///

"""
Run full test suite when stopping.

This hook runs the full test suite when stopping to ensure all tests pass.
Runs on Stop and SubagentStop events.
"""

import asyncio
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from hook_logging import hook_invocation


async def run_tests(package_manager: str, cwd: str) -> tuple[int, str, str]:
    args = [package_manager]
    if package_manager == "npm":
        args.append("test")
    else:
        args.extend(["run", "test"])

    try:
        proc = await asyncio.create_subprocess_exec(
            *args,
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout_bytes, stderr_bytes = await asyncio.wait_for(
            proc.communicate(), timeout=300
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

    package_json = project_root / "package.json"
    if not package_json.exists():
        print("[Warning] package.json not found, skipping test suite", file=sys.stderr)
        return 0

    try:
        pkg_data = json.loads(package_json.read_text())
    except json.JSONDecodeError:
        print("[Error] Invalid package.json", file=sys.stderr)
        return 1

    scripts = pkg_data.get("scripts", {})
    if "test" not in scripts:
        print("[Warning] No test script found in package.json", file=sys.stderr)
        return 0

    print("[Progress] Running test suite...", file=sys.stderr)

    package_manager = "npm"
    for pm in ["pnpm", "yarn", "bun"]:
        if shutil.which(pm):
            package_manager = pm
            break

    exit_code, stdout, stderr = await run_tests(package_manager, cwd)

    if exit_code == 0:
        print("[Success] All tests passed", file=sys.stderr)
    else:
        print("[Error] Tests failed", file=sys.stderr)
        details = stderr[:500] if stderr else stdout[:500]
        print(f"  Details: {details}", file=sys.stderr)
        print("  Hints:", file=sys.stderr)
        print("    - Review test failures above", file=sys.stderr)
        print("    - Run tests locally to debug", file=sys.stderr)

    return exit_code


def main() -> None:
    with hook_invocation("test_project") as inv:
        try:
            payload = json.load(sys.stdin)
        except json.JSONDecodeError:
            sys.exit(0)

        inv.set_payload(payload)
        sys.exit(asyncio.run(main_async(payload)))


if __name__ == "__main__":
    main()
```
