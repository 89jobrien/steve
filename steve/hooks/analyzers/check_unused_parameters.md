---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: hook
---

# Check Unused Parameters

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///

"""Detect lazy refactoring with underscore-prefixed params.

This hook prevents adding underscore-prefixed unused parameters.
Runs after Edit or MultiEdit operations.
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from hook_logging import hook_invocation


def find_unused_parameters(code: str) -> list[str]:
    unused = []

    function_patterns = [
        r"function\s+\w+\s*\(([^)]+)\)",
        r"const\s+\w+\s*=\s*\(([^)]+)\)\s*=>",
        r"(?:async\s+)?function\s*\(([^)]+)\)",
        r"\w+\s*\(([^)]+)\)\s*{",
        r"def\s+\w+\s*\(([^)]+)\)",
    ]

    for pattern in function_patterns:
        matches = re.finditer(pattern, code, re.MULTILINE)
        for match in matches:
            params_str = match.group(1)
            params = [p.strip() for p in params_str.split(",") if p.strip()]

            for param in params:
                param_name = param.split(":")[0].split("=")[0].strip()

                if param_name.startswith("_") and not param_name.startswith("__"):
                    unused.append(param_name)

    return unused


def main() -> None:
    with hook_invocation("check_unused_parameters") as inv:
        try:
            payload = json.load(sys.stdin)
        except json.JSONDecodeError:
            sys.exit(0)

        inv.set_payload(payload)

        if payload.get("stop_hook_active"):
            sys.exit(0)

        tool_name = payload.get("tool_name")
        if tool_name not in ["Edit", "MultiEdit"]:
            sys.exit(0)

        tool_input = payload.get("tool_input", {})
        if not tool_input or not isinstance(tool_input, dict):
            sys.exit(0)

        new_string = tool_input.get("new_string", "")
        if not new_string:
            sys.exit(0)

        unused_params = find_unused_parameters(new_string)

        if unused_params:
            print("[Error] Unused parameters detected", file=sys.stderr)
            print(
                f"  Details: Found {len(unused_params)} parameter(s) with underscore prefix",
                file=sys.stderr,
            )
            print("  Hints:", file=sys.stderr)
            print(
                "    - Remove unused parameters instead of prefixing with underscore",
                file=sys.stderr,
            )
            print(
                "    - If the parameter is required by an interface, document why",
                file=sys.stderr,
            )
            print(
                "    - Consider refactoring to eliminate the need for unused parameters",
                file=sys.stderr,
            )

            for param in unused_params:
                print(f"  {param}", file=sys.stderr)

            sys.exit(1)

        sys.exit(0)


if __name__ == "__main__":
    main()
```
