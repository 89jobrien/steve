#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///

"""Check for 'any' types in TypeScript files.

This hook forbids 'any' types in TypeScript files to enforce better type safety.
Runs after Write, Edit, or MultiEdit operations on .ts/.tsx files.
"""

import json
import re
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent.parent))
from hook_logging import hook_invocation


def should_skip_file(file_path: str | None, extensions: list[str]) -> bool:
    if not file_path:
        return True
    path = Path(file_path)
    return path.suffix not in extensions


def check_any_types(file_path: str) -> tuple[int, list[tuple[int, str]]]:
    try:
        content = Path(file_path).read_text()
    except FileNotFoundError:
        return 0, []

    any_patterns = [
        r":\s*any\b",
        r"\bas\s+any\b",
        r"<any>",
        r"<any,",
        r",\s*any>",
        r"Array<any>",
    ]

    test_utility_patterns = [
        r"expect\.any\(",
        r"\.any\(\)",
    ]

    lines_with_any = []
    for line_num, line in enumerate(content.split("\n"), 1):
        has_any = any(re.search(pattern, line) for pattern in any_patterns)
        is_test_utility = any(re.search(pattern, line) for pattern in test_utility_patterns)
        if has_any and not is_test_utility:
            lines_with_any.append((line_num, line.strip()))

    return 1 if lines_with_any else 0, lines_with_any


def main() -> None:
    with hook_invocation("check_any_changed") as inv:
        try:
            payload = json.load(sys.stdin)
        except json.JSONDecodeError:
            sys.exit(0)

        inv.set_payload(payload)

        if payload.get("stop_hook_active"):
            sys.exit(0)

        tool_input = payload.get("tool_input", {})
        file_path = tool_input.get("file_path") if isinstance(tool_input, dict) else None

        if should_skip_file(file_path, [".ts", ".tsx"]):
            sys.exit(0)

        if not file_path:
            sys.exit(0)

        exit_code, lines_with_any = check_any_types(file_path)

        if lines_with_any:
            file_name = Path(file_path).name
            print("[Error] TypeScript 'any' types detected", file=sys.stderr)
            print(
                f"  Details: Found {len(lines_with_any)} occurrence(s) in {file_name}",
                file=sys.stderr,
            )
            print("  Hints:", file=sys.stderr)
            print(
                "    - Replace 'any' with 'unknown' for better type safety",
                file=sys.stderr,
            )
            print("    - Use specific types when possible", file=sys.stderr)
            print("    - Consider using generics for flexible types", file=sys.stderr)

            for line_num, line in lines_with_any:
                print(f"  Line {line_num}: {line}", file=sys.stderr)

        sys.exit(exit_code)


if __name__ == "__main__":
    main()
