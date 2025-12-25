---
name: test-changed
description: Run tests for changed files when saving.
author: Joseph OBrien
status: unpublished
updated: 2025-12-23
version: 1.0.1
tag: hook
---
# Test Changed

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///

"""
Run tests for changed files when saving.

This hook finds and runs tests for changed files automatically.
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


def find_test_files(file_path: Path, project_root: Path) -> list[str]:
    test_files = []

    stem = file_path.stem
    parent = file_path.parent

    test_patterns = [
        parent / f"test_{stem}.py",
        parent / f"{stem}_test.py",
        parent / f"{stem}.test.ts",
        parent / f"{stem}.test.tsx",
        parent / f"{stem}.spec.ts",
        parent / f"{stem}.spec.tsx",
        project_root / "tests" / f"test_{stem}.py",
        project_root / "__tests__" / f"{stem}.test.ts",
    ]

    for pattern in test_patterns:
        if pattern.exists():
            test_files.append(str(pattern))

    return test_files


def detect_test_runner(project_root: Path) -> str | None:
    if (
        (project_root / "pytest.ini").exists()
        or (project_root / "pyproject.toml").exists()
    ) and command_exists("pytest"):
        return "pytest"

    if (
        (project_root / "jest.config.js").exists()
        or (project_root / "jest.config.ts").exists()
    ) and command_exists("jest"):
        return "jest"

    if (project_root / "vitest.config.ts").exists() and command_exists("vitest"):
        return "vitest"

    return None


async def run_tests(
    test_runner: str, test_files: list[str], cwd: str
) -> tuple[int, str, str]:
    if test_runner == "pytest":
        args = ["pytest", "-v"] + test_files
    elif test_runner == "jest":
        args = ["jest"] + test_files
    elif test_runner == "vitest":
        args = ["vitest", "run"] + test_files
    else:
        return 1, "", "Unknown test runner"

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

    tool_input = payload.get("tool_input", {})
    file_path = tool_input.get("file_path") if isinstance(tool_input, dict) else None

    if not file_path:
        return 0

    path = Path(file_path)
    if not path.exists():
        return 0

    cwd = payload.get("cwd", ".")
    project_root = Path(cwd)

    test_files = find_test_files(path, project_root)
    if not test_files:
        return 0

    test_runner = detect_test_runner(project_root)
    if not test_runner:
        return 0

    print(f"[Progress] Running tests for {path.name}", file=sys.stderr)

    exit_code, stdout, stderr = await run_tests(test_runner, test_files, cwd)

    if exit_code != 0:
        print("[Error] Tests failed", file=sys.stderr)
        print(f"  Details: Test runner exited with code {exit_code}", file=sys.stderr)
        print("  Hints:", file=sys.stderr)
        print("    - Fix failing tests before continuing", file=sys.stderr)
        print("    - Review test output above for details", file=sys.stderr)
        print("    - Run tests locally to debug", file=sys.stderr)

        if stdout:
            print(stdout, file=sys.stderr)
        if stderr:
            print(stderr, file=sys.stderr)

        return 1

    print("[Success] All tests passed", file=sys.stderr)
    return 0


def main() -> None:
    with hook_invocation("test_changed") as inv:
        try:
            payload = json.load(sys.stdin)
        except json.JSONDecodeError:
            sys.exit(0)

        inv.set_payload(payload)
        sys.exit(asyncio.run(main_async(payload)))


if __name__ == "__main__":
    main()
```
