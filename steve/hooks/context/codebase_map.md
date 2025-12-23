---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: hook
---

# Codebase Map

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///

"""
Add codebase map to context at session start.

This hook generates a tree structure of the codebase for context.
Runs on SessionStart and UserPromptSubmit events (once per session).
"""

import json
import sys
from fnmatch import fnmatch
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from hook_logging import hook_invocation

SESSION_CACHE: set[str] = set()


def matches_include_pattern(
    entry: Path, include_patterns: list[str], project_root: Path
) -> bool:
    """Check if entry matches any include pattern."""
    # Get relative path from project root
    try:
        rel_path = entry.relative_to(project_root)
    except ValueError:
        return False

    rel_str = str(rel_path)
    rel_str_forward = rel_str.replace("\\", "/")  # Normalize to forward slashes

    for pattern in include_patterns:
        pattern_normalized = pattern.replace("\\", "/")

        # Exact name match
        if entry.name == pattern:
            return True

        # Match against relative path directly
        if fnmatch(rel_str_forward, pattern_normalized):
            return True

        # Match against name with glob
        if fnmatch(entry.name, pattern_normalized):
            return True

        # Match if entry is under a directory pattern (e.g., "nathan/**" matches "nathan/file.py")
        if pattern_normalized.endswith("/**"):
            dir_pattern = pattern_normalized[:-3]  # Remove "/**"
            if rel_str_forward == dir_pattern or rel_str_forward.startswith(
                dir_pattern + "/"
            ):
                return True
        elif "/" in pattern_normalized or pattern_normalized.endswith("*"):
            # Pattern with path separators - check if entry path matches
            if fnmatch(rel_str_forward, pattern_normalized) or fnmatch(
                rel_str_forward, f"**/{pattern_normalized}"
            ):
                return True

    return False


def generate_tree(
    root: Path,
    max_depth: int,
    include_patterns: list[str],
    project_root: Path,
    current_depth: int = 0,
    prefix: str = "",
) -> str:
    if current_depth >= max_depth:
        return ""

    try:
        entries = sorted(
            root.iterdir(),
            key=lambda p: (not p.is_dir(), p.name.lower()),
        )
    except PermissionError:
        return ""

    lines = []
    # Only include entries that match the include patterns
    entries = [
        e for e in entries if matches_include_pattern(e, include_patterns, project_root)
    ]

    for i, entry in enumerate(entries):
        is_last = i == len(entries) - 1
        connector = "└── " if is_last else "├── "
        lines.append(f"{prefix}{connector}{entry.name}")

        if entry.is_dir():
            extension = "    " if is_last else "│   "
            subtree = generate_tree(
                entry,
                max_depth,
                include_patterns,
                project_root,
                current_depth + 1,
                prefix + extension,
            )
            if subtree:
                lines.append(subtree)

    return "\n".join(lines)


def main() -> None:
    with hook_invocation("codebase_map") as inv:
        try:
            payload = json.load(sys.stdin)
        except json.JSONDecodeError:
            sys.exit(0)

        inv.set_payload(payload)

        if payload.get("stop_hook_active"):
            sys.exit(0)

        session_id = payload.get("session_id", "default")

        if session_id in SESSION_CACHE:
            sys.exit(0)

        cwd = payload.get("cwd", ".")
        project_root = Path(cwd)

        if not project_root.exists():
            sys.exit(0)

        max_depth = 3
        # Only include directories/files explicitly listed
        # Supports glob patterns: "nathan/**", "*.py", "docs/*", etc.
        include_patterns = [
            "nathan",
            "nathan/**",
            "tests",
            "tests/**",
            "docs",
            "docs/**",
            "scripts",
            "scripts/**",
            "*.py",
            "*.md",
            "*.toml",
            "*.yaml",
            "*.yml",
            "*.json",
            "*.sh",
            "pyproject.toml",
            "README.md",
            "docker-compose*.yml",
        ]

        print("[Progress] Generating codebase map...", file=sys.stderr)

        codebase_map = generate_tree(
            project_root, max_depth, include_patterns, project_root
        )

        print("[Success] Codebase map generated", file=sys.stderr)
        print("\n" + "=" * 60)
        print("CODEBASE STRUCTURE")
        print("=" * 60)
        print(codebase_map)
        print("=" * 60 + "\n")

        SESSION_CACHE.add(session_id)

        sys.exit(0)


if __name__ == "__main__":
    main()
```
