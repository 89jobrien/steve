#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///

"""
Validate Bash commands with shellcheck before execution.

This hook runs shellcheck on Bash tool commands to catch syntax errors,
common mistakes, and potential issues before execution.
Runs before Bash tool execution (PreToolUse).
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Literal

sys.path.insert(0, str(Path(__file__).parent.parent))
from hook_logging import hook_invocation


def check_shellcheck_installed() -> bool:
    """Check if shellcheck is available."""
    try:
        subprocess.run(
            ["shellcheck", "--version"],
            capture_output=True,
            check=False,
            timeout=2,
        )
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def run_shellcheck(
    command: str,
) -> tuple[Literal["pass", "warning", "error"], list[str]]:
    """
    Run shellcheck on the command and return result.

    Returns:
        ("pass", []): No issues found
        ("warning", [messages]): Warnings found
        ("error", [messages]): Errors found
    """
    if not check_shellcheck_installed():
        return "pass", ["shellcheck not installed, skipping validation"]

    # Write command to temporary file
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".sh", delete=False
    ) as tmp_file:
        # Add shebang for proper shellcheck analysis
        tmp_file.write("#!/usr/bin/env bash\n")
        tmp_file.write("set -euo pipefail\n\n")
        tmp_file.write(command)
        tmp_path = Path(tmp_file.name)

    try:
        # Run shellcheck with JSON output for easier parsing
        result = subprocess.run(
            [
                "shellcheck",
                "--format=json",
                "--severity=warning",  # Report warnings and above
                "--exclude=SC2317",  # Exclude "unreachable code" (common in hooks)
                str(tmp_path),
            ],
            capture_output=True,
            text=True,
            timeout=5,
        )

        # Parse JSON output
        try:
            issues = json.loads(result.stdout)
        except json.JSONDecodeError:
            # Fallback if JSON parsing fails
            return "pass", []

        if not issues:
            return "pass", []

        # Categorize issues by severity
        errors = [
            issue for issue in issues if issue.get("level") in ("error", "warning")
        ]
        warnings = [issue for issue in issues if issue.get("level") == "info"]

        messages = []
        for issue in errors + warnings:
            line = issue.get("line", 0)
            code = issue.get("code", "")
            message = issue.get("message", "")
            # Adjust line number to account for added shebang/set lines
            actual_line = max(1, line - 2)
            messages.append(f"Line {actual_line} (SC{code}): {message}")

        if errors:
            return "error", messages
        if warnings:
            return "warning", messages

        return "pass", []

    except subprocess.TimeoutExpired:
        return "warning", ["shellcheck timed out (command may be too complex)"]
    except Exception as e:
        return "warning", [f"shellcheck validation failed: {e!s}"]
    finally:
        # Clean up temp file
        tmp_path.unlink(missing_ok=True)


def check_command(command: str) -> tuple[str | None, list[str]]:
    """
    Check Bash command with shellcheck.

    Returns:
        (None, []): Command is valid
        (error_message, hints): Command has issues
    """
    if not command or not command.strip():
        return None, []

    status, messages = run_shellcheck(command)

    if status == "pass":
        return None, []

    if status == "error":
        error_summary = f"shellcheck found {len(messages)} issue(s)"
        hints = messages + [
            "Fix these issues before running the command",
            "Run 'shellcheck' manually for more details",
        ]
        return error_summary, hints

    if status == "warning":
        # For warnings, we don't block but provide feedback
        return None, []

    return None, []


def main() -> None:
    with hook_invocation("shellcheck_guard") as inv:
        try:
            payload = json.load(sys.stdin)
        except json.JSONDecodeError:
            sys.exit(0)

        inv.set_payload(payload)

        tool_input = payload.get("tool_input", {})
        command = tool_input.get("command") if isinstance(tool_input, dict) else None

        if not command:
            sys.exit(0)

        error_msg, hints = check_command(command)

        if error_msg:
            print(f"[Error] {error_msg}", file=sys.stderr)
            print(f"  Command: {command[:100]}...", file=sys.stderr)
            if hints:
                print("  Issues:", file=sys.stderr)
                for hint in hints:
                    print(f"    - {hint}", file=sys.stderr)
            sys.exit(2)  # Block execution

        sys.exit(0)


if __name__ == "__main__":
    main()
