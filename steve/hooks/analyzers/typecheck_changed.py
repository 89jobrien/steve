#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///

"""Run TypeScript type checking on changed files.

This hook runs TypeScript compiler on changed .ts/.tsx files.
Runs after Write, Edit, or MultiEdit operations.
"""

import asyncio
import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent.parent))
from hook_logging import hook_invocation


def should_skip_file(file_path: str | None, extensions: list[str]) -> bool:
    if not file_path:
        return True
    path = Path(file_path)
    return path.suffix not in extensions


def parse_tsc_output(output: str) -> list[str]:
    lines = output.split("\n")
    errors = []

    for line in lines:
        line = line.strip()
        if line and ("error TS" in line or ": error" in line):
            errors.append(line)

    return errors


async def run_typecheck(file_path: str, cwd: str) -> tuple[int, str, str]:
    args = ["npx", "tsc", "--noEmit", str(file_path)]

    try:
        proc = await asyncio.create_subprocess_exec(
            *args,
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout_bytes, stderr_bytes = await asyncio.wait_for(proc.communicate(), timeout=60)
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

    tool_input = payload.get("tool_input", {})
    file_path = tool_input.get("file_path") if isinstance(tool_input, dict) else None

    if should_skip_file(file_path, [".ts", ".tsx"]):
        return 0

    if not file_path:
        return 0

    cwd = payload.get("cwd", ".")
    project_root = Path(cwd)

    tsconfig = project_root / "tsconfig.json"
    if not tsconfig.exists():
        return 0

    path = Path(file_path)
    if not path.exists():
        return 0

    print(f"[Progress] Type checking {path.name}...", file=sys.stderr)

    exit_code, stdout, stderr = await run_typecheck(file_path, cwd)

    if exit_code == 0:
        print("[Success] Type checking passed", file=sys.stderr)
    else:
        output = stderr if stderr else stdout
        errors = parse_tsc_output(output)

        if errors:
            print(f"[Error] Type errors found in {path.name}", file=sys.stderr)
            print(f"  Details: {errors[0] if errors else 'See output'}", file=sys.stderr)
            print("  Hints:", file=sys.stderr)
            print("    - Fix type errors before continuing", file=sys.stderr)
            print("    - Run 'npm run type-check' to see all errors", file=sys.stderr)
        else:
            print("[Error] Type checking failed", file=sys.stderr)
            print(f"  Details: {output[:200]}", file=sys.stderr)

    return exit_code


def main() -> None:
    with hook_invocation("typecheck_changed") as inv:
        try:
            payload = json.load(sys.stdin)
        except json.JSONDecodeError:
            sys.exit(0)

        inv.set_payload(payload)
        sys.exit(asyncio.run(main_async(payload)))


if __name__ == "__main__":
    main()
