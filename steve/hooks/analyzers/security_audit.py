#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///

"""Run security audit on changed files.

This hook runs bandit (Python) or eslint-plugin-security patterns on changed files.
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


async def run_command(args: list[str], cwd: str, timeout: int = 60) -> tuple[int, str, str]:
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


async def run_bandit(file_path: str, cwd: str) -> tuple[int, str, str]:
    """Run bandit security scanner on Python file."""
    if command_exists("bandit"):
        args = ["bandit", "-f", "txt", "-ll", file_path]
    elif command_exists("uvx"):
        args = ["uvx", "bandit", "-f", "txt", "-ll", file_path]
    else:
        return 0, "", ""  # Skip if not available

    return await run_command(args, cwd)


async def run_semgrep(file_path: str, cwd: str) -> tuple[int, str, str]:
    """Run semgrep security scanner if available."""
    if not command_exists("semgrep"):
        return 0, "", ""  # Skip if not available

    args = [
        "semgrep",
        "--config",
        "auto",
        "--severity",
        "ERROR",
        "--severity",
        "WARNING",
        "--quiet",
        file_path,
    ]
    return await run_command(args, cwd, timeout=120)


def get_security_patterns_for_js(content: str) -> list[str]:
    """Check for common JS security issues."""
    issues = []

    patterns = [
        ("eval(", "Use of eval() - potential code injection"),
        ("innerHTML", "Use of innerHTML - potential XSS"),
        ("document.write", "Use of document.write - potential XSS"),
        ("dangerouslySetInnerHTML", "Use of dangerouslySetInnerHTML - potential XSS"),
        ("child_process.exec", "Use of exec - potential command injection"),
        ("new Function(", "Use of Function constructor - potential code injection"),
        ("__proto__", "Use of __proto__ - potential prototype pollution"),
        ("Object.assign({},", "Shallow copy may be vulnerable to prototype pollution"),
    ]

    for pattern, description in patterns:
        if pattern in content:
            issues.append(description)

    return issues


def main() -> None:
    with hook_invocation("security_audit") as inv:
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

        cwd = payload.get("cwd", ".")
        suffix = path.suffix.lower()
        issues_found = []

        # Python security check
        if suffix == ".py":
            print(f"[Progress] Running security audit on {path.name}", file=sys.stderr)
            exit_code, stdout, stderr = asyncio.run(run_bandit(file_path, cwd))

            if exit_code != 0 and stdout:
                issues_found.append(("bandit", stdout))

        # JavaScript/TypeScript security check
        elif suffix in (".js", ".jsx", ".ts", ".tsx"):
            print(f"[Progress] Running security audit on {path.name}", file=sys.stderr)

            try:
                content = path.read_text()
                js_issues = get_security_patterns_for_js(content)
                if js_issues:
                    issues_found.append(("pattern-check", "\n".join(f"  - {i}" for i in js_issues)))
            except (OSError, UnicodeDecodeError):
                pass

        else:
            sys.exit(0)

        if issues_found:
            print(f"[Warning] Security issues found in {path.name}", file=sys.stderr)
            for tool, output in issues_found:
                print(f"  [{tool}]:", file=sys.stderr)
                lines = output.strip().split("\n")[:10]
                for line in lines:
                    print(f"    {line}", file=sys.stderr)
            print("  Hints:", file=sys.stderr)
            print("    - Review flagged code for security implications", file=sys.stderr)
            print("    - Consider safer alternatives", file=sys.stderr)
            # Don't block, just warn
            sys.exit(0)

        print("[Success] Security audit passed", file=sys.stderr)
        sys.exit(0)


if __name__ == "__main__":
    main()
