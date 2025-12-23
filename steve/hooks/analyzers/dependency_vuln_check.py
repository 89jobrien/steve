#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///

"""Check for dependency vulnerabilities when package files change.

This hook runs vulnerability checks when package.json, pyproject.toml, etc. change.
Runs after Write, Edit, or MultiEdit operations (PostToolUse).
"""

import asyncio
import json
import shutil
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent.parent))
from hook_logging import hook_invocation


# Files that trigger vulnerability checks
PACKAGE_FILES = [
    "package.json",
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "pyproject.toml",
    "requirements.txt",
    "requirements-dev.txt",
    "Pipfile",
    "Pipfile.lock",
    "poetry.lock",
    "Gemfile",
    "Gemfile.lock",
    "go.mod",
    "go.sum",
    "Cargo.toml",
    "Cargo.lock",
]


def command_exists(cmd: str) -> bool:
    return shutil.which(cmd) is not None


async def run_command(args: list[str], cwd: str, timeout: int = 120) -> tuple[int, str, str]:
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


async def check_npm_audit(cwd: str) -> tuple[bool, str]:
    """Run npm audit for Node.js projects."""
    if not command_exists("npm"):
        return True, ""

    exit_code, stdout, stderr = await run_command(["npm", "audit", "--json"], cwd, timeout=60)

    if exit_code != 0:
        # Parse JSON to get summary
        try:
            data = json.loads(stdout)
            vulns = data.get("metadata", {}).get("vulnerabilities", {})
            critical = vulns.get("critical", 0)
            high = vulns.get("high", 0)
            if critical or high:
                return False, f"Found {critical} critical, {high} high vulnerabilities"
        except json.JSONDecodeError:
            pass
        return False, "npm audit found vulnerabilities"

    return True, ""


async def check_pip_audit(cwd: str) -> tuple[bool, str]:
    """Run pip-audit for Python projects."""
    args = []
    if command_exists("pip-audit"):
        args = ["pip-audit"]
    elif command_exists("uvx"):
        args = ["uvx", "pip-audit"]
    else:
        return True, ""  # Skip if not available

    exit_code, stdout, stderr = await run_command(args, cwd, timeout=120)

    if exit_code != 0:
        lines = stdout.strip().split("\n")
        vuln_count = len([line for line in lines if line.strip() and not line.startswith("Name")])
        if vuln_count > 0:
            return False, f"pip-audit found {vuln_count} vulnerabilities"

    return True, ""


def get_checker_for_file(filename: str) -> str | None:
    """Determine which vulnerability checker to use."""
    npm_files = ["package.json", "package-lock.json", "yarn.lock", "pnpm-lock.yaml"]
    python_files = [
        "pyproject.toml",
        "requirements.txt",
        "requirements-dev.txt",
        "Pipfile",
        "Pipfile.lock",
        "poetry.lock",
    ]

    if filename in npm_files:
        return "npm"
    if filename in python_files:
        return "pip"

    return None


def main() -> None:
    with hook_invocation("dependency_vuln_check") as inv:
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
        filename = path.name

        # Check if this is a package file
        if filename not in PACKAGE_FILES:
            sys.exit(0)

        cwd = payload.get("cwd", ".")
        checker = get_checker_for_file(filename)

        if not checker:
            sys.exit(0)

        print("[Progress] Checking for dependency vulnerabilities...", file=sys.stderr)

        if checker == "npm":
            ok, message = asyncio.run(check_npm_audit(cwd))
        elif checker == "pip":
            ok, message = asyncio.run(check_pip_audit(cwd))
        else:
            sys.exit(0)

        if not ok:
            print(f"[Warning] {message}", file=sys.stderr)
            print("  Hints:", file=sys.stderr)
            print(
                "    - Run 'npm audit fix' or 'pip-audit --fix' to auto-fix",
                file=sys.stderr,
            )
            print("    - Review vulnerabilities and update dependencies", file=sys.stderr)
            # Don't block, just warn
            sys.exit(0)

        print("[Success] No known vulnerabilities found", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
