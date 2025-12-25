---
name: self-review
description: Prompt critical self-review.
author: Joseph OBrien
status: unpublished
updated: 2025-12-23
version: 1.0.1
tag: hook
---
# Self Review

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///

"""
Prompt critical self-review.

This hook checks if a session included self-review markers.
Runs on Stop and SubagentStop events.
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from hook_logging import hook_invocation


def check_for_self_review_marker(content: str) -> bool:
    markers = [
        "self-review",
        "critical review",
        "implementation complete",
        "testing complete",
        "edge cases considered",
    ]

    content_lower = content.lower()
    return any(marker in content_lower for marker in markers)


def generate_review_questions(file_path: str | None) -> list[str]:
    questions = [
        "Have all requested features been fully implemented?",
        "Are error cases and edge conditions properly handled?",
        "Have you tested the implementation with various inputs?",
        "Is the code documented and readable?",
        "Are there any performance or security concerns?",
    ]

    if file_path:
        path = Path(file_path)
        if path.suffix in [".py", ".ts", ".js"]:
            questions.extend(
                [
                    "Are type hints/types properly defined?",
                    "Is there adequate test coverage?",
                ]
            )

    return questions


def main() -> None:
    with hook_invocation("self_review") as inv:
        try:
            payload = json.load(sys.stdin)
        except json.JSONDecodeError:
            sys.exit(0)

        inv.set_payload(payload)

        if payload.get("stop_hook_active"):
            sys.exit(0)

        transcript_path = payload.get("transcript_path")
        if not transcript_path:
            sys.exit(0)

        path = Path(transcript_path)
        if not path.exists():
            sys.exit(0)

        try:
            content = path.read_text()
        except (OSError, FileNotFoundError):
            sys.exit(0)

        has_self_review = check_for_self_review_marker(content)

        if has_self_review:
            sys.exit(0)

        tool_input = payload.get("tool_input", {})
        file_path = (
            tool_input.get("file_path") if isinstance(tool_input, dict) else None
        )

        review_questions = generate_review_questions(file_path)

        print("[Warning] No self-review detected in session", file=sys.stderr)
        print("[Progress] Consider reviewing the following:", file=sys.stderr)
        for question in review_questions:
            print(f"  - {question}", file=sys.stderr)

        sys.exit(0)


if __name__ == "__main__":
    main()
```
