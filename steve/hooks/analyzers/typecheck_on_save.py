#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///

"""Run type checking on changed files.

This hook runs mypy (Python) or tsc (TypeScript) on changed files.
Runs after Write, Edit, or MultiEdit operations (PostToolUse).
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


def detect_type_checker(project_root: Path, file_path: Path) -> tuple[str | None, list[str]]:
    """Detect appropriate type checker and return command args."""
    suffix = file_path.suffix.lower()

    # Python files
    if suffix == ".py":
        if (project_root / "pyproject.toml").exists() or (project_root / "mypy.ini").exists():
            if command_exists("mypy"):
                return "mypy", ["mypy", str(file_path)]
            # Try uvx mypy
            if command_exists("uvx"):
                return "mypy (uvx)", ["uvx", "mypy", str(file_path)]
        return None, []

    # TypeScript files
    if suffix in (".ts", ".tsx"):
        tsconfig = project_root / "tsconfig.json"
        if tsconfig.exists():
            if command_exists("tsc"):
                return "tsc", ["tsc", "--noEmit", "-p", str(tsconfig)]
            # Try npx tsc
            if command_exists("npx"):
                return "tsc (npx)", ["npx", "tsc", "--noEmit", "-p", str(tsconfig)]
        return None, []

    return None, []


async def run_type_checker(args: list[str], cwd: str, timeout: int = 60) -> tuple[int, str, str]:
    try:
        proc = await asyncio.create_subprocess_exec(
            *args,
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout_bytes, stderr_bytes = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        return (
            proc.returncode or 0,
            stdout_bytes.decode("utf-8", errors="replace"),
            stderr_bytes.decode("utf-8", errors="replace"),
        )
    except (FileNotFoundError, TimeoutError, OSError) as e:
        return 1, "", str(e)


def main() -> None:
    with hook_invocation("typecheck_on_save") as inv:
        try:
            payload = json.load(sys.stdin)
        except json.JSONDecodeError:
            sys.exit(0)

        inv.set_payload(payload)

        if payload.get("stop_hook_active"):
            sys.exit(0)

        tool_input = payload.get("tool_input", {})
        file_path = tool_input.get("file_path") if isinstance(tool_input, dict) else None

        if not file_path:
            sys.exit(0)

        path = Path(file_path)
        if not path.exists():
            sys.exit(0)

        # Only check Python and TypeScript files
        if path.suffix.lower() not in (".py", ".ts", ".tsx"):
            sys.exit(0)

        cwd = payload.get("cwd", ".")
        project_root = Path(cwd)

        checker_name, args = detect_type_checker(project_root, path)
        if not checker_name:
            sys.exit(0)

        print(f"[Progress] Running {checker_name} on {path.name}", file=sys.stderr)

        exit_code, stdout, stderr = asyncio.run(run_type_checker(args, cwd))

        if exit_code != 0:
            print(f"[Error] {checker_name} found type errors", file=sys.stderr)
            print(f"  File: {path.name}", file=sys.stderr)

            # Show relevant output
            output = stdout or stderr
            if output:
                lines = output.strip().split("\n")[:10]  # Limit output
                for line in lines:
                    print(f"  {line}", file=sys.stderr)

            print("  Hints:", file=sys.stderr)
            print("    - Fix type annotations", file=sys.stderr)
            print("    - Add type: ignore comment if false positive", file=sys.stderr)
            sys.exit(1)

        print(f"[Success] {checker_name} passed", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
