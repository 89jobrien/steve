---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: hook
---

# Typecheck Project

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///

"""
Run TypeScript validation on entire project.

This hook runs TypeScript compiler on the entire project.
Runs on Stop and SubagentStop events.
"""

import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from hook_logging import hook_invocation


def parse_tsc_output(output: str) -> list[str]:
    lines = output.split("\n")
    errors = []

    for line in lines:
        line = line.strip()
        if line and ("error TS" in line or ": error" in line):
            errors.append(line)

    return errors


async def run_typecheck(cwd: str) -> tuple[int, str, str]:
    args = ["npx", "tsc", "--noEmit"]

    try:
        proc = await asyncio.create_subprocess_exec(
            *args,
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout_bytes, stderr_bytes = await asyncio.wait_for(
            proc.communicate(), timeout=120
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

    tsconfig = project_root / "tsconfig.json"
    if not tsconfig.exists():
        print(
            "[Warning] tsconfig.json not found, skipping type checking", file=sys.stderr
        )
        return 0

    print("[Progress] Running TypeScript type checking...", file=sys.stderr)

    exit_code, stdout, stderr = await run_typecheck(cwd)

    if exit_code == 0:
        print("[Success] No type errors found", file=sys.stderr)
    else:
        output = stderr if stderr else stdout
        errors = parse_tsc_output(output)

        error_count = len(errors)
        if error_count > 0:
            print(f"[Error] Found {error_count} type error(s)", file=sys.stderr)
            print(f"  Details: {chr(10).join(errors[:5])}", file=sys.stderr)
            print("  Hints:", file=sys.stderr)
            print("    - Review type errors above", file=sys.stderr)
            print(
                "    - Run 'npx tsc --noEmit' locally for full output", file=sys.stderr
            )
        else:
            print("[Error] Type checking failed", file=sys.stderr)
            print(f"  Details: {output[:300]}", file=sys.stderr)

    return exit_code


def main() -> None:
    with hook_invocation("typecheck_project") as inv:
        try:
            payload = json.load(sys.stdin)
        except json.JSONDecodeError:
            sys.exit(0)

        inv.set_payload(payload)
        sys.exit(asyncio.run(main_async(payload)))


if __name__ == "__main__":
    main()
```
