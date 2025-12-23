---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: hook
---

# Cleanup Handler

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///

"""
Clean up temporary files and resources at end of session.

This hook removes temp files, debug artifacts, and other session debris.
Runs on Stop event.
"""

import json
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from hook_logging import hook_invocation

# Patterns for files to clean up
CLEANUP_PATTERNS = [
    # Temporary files
    "*.tmp",
    "*.temp",
    "*.bak",
    "*.swp",
    "*.swo",
    "*~",
    # Python artifacts
    "__pycache__",
    "*.pyc",
    "*.pyo",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    # Node artifacts
    ".eslintcache",
    ".parcel-cache",
    # Debug files
    "debug.log",
    "*.debug",
    ".debug/",
]

# Directories to clean (relative to cwd)
CLEANUP_DIRS = [
    ".claude-temp",
    ".ai-temp",
    "tmp",
]

# Max age for old session logs (days)
MAX_LOG_AGE_DAYS = 7


def cleanup_old_session_logs() -> int:
    """Clean up old session logs and summaries."""
    cleaned = 0
    cutoff = datetime.now() - timedelta(days=MAX_LOG_AGE_DAYS)

    dirs_to_clean = [
        Path.home() / ".claude" / "session-logs",
        Path.home() / ".claude" / "session-summaries",
        Path.home() / ".claude" / "session-diffs",
    ]

    for log_dir in dirs_to_clean:
        if not log_dir.exists():
            continue

        try:
            for file in log_dir.iterdir():
                if file.is_file():
                    mtime = datetime.fromtimestamp(file.stat().st_mtime)
                    if mtime < cutoff:
                        file.unlink()
                        cleaned += 1
        except OSError:
            pass

    return cleaned


def cleanup_temp_files(cwd: str) -> int:
    """Clean up temporary files in the working directory."""
    cleaned = 0
    project_root = Path(cwd)

    # Clean specific temp directories
    for dir_name in CLEANUP_DIRS:
        temp_dir = project_root / dir_name
        if temp_dir.exists() and temp_dir.is_dir():
            try:
                import shutil

                shutil.rmtree(temp_dir)
                cleaned += 1
            except OSError:
                pass

    # Clean temp files (only in root, not recursive for safety)
    temp_extensions = [".tmp", ".temp", ".bak"]
    try:
        for file in project_root.iterdir():
            if file.is_file() and file.suffix in temp_extensions:
                try:
                    file.unlink()
                    cleaned += 1
                except OSError:
                    pass
    except OSError:
        pass

    return cleaned


def cleanup_empty_dirs(cwd: str) -> int:
    """Remove empty directories that might have been left behind."""
    cleaned = 0
    project_root = Path(cwd)

    # Only clean known artifact directories
    artifact_dirs = ["__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"]

    for artifact in artifact_dirs:
        for match in project_root.rglob(artifact):
            if match.is_dir():
                try:
                    # Check if empty or only contains __pycache__ type files
                    contents = list(match.iterdir())
                    if not contents or all(
                        f.suffix in [".pyc", ".pyo"] for f in contents if f.is_file()
                    ):
                        import shutil

                        shutil.rmtree(match)
                        cleaned += 1
                except OSError:
                    pass

    return cleaned


def main() -> None:
    with hook_invocation("cleanup_handler") as inv:
        try:
            payload = json.load(sys.stdin)
        except json.JSONDecodeError:
            sys.exit(0)

        inv.set_payload(payload)

        if payload.get("stop_hook_active"):
            sys.exit(0)

        cwd = payload.get("cwd", ".")

        total_cleaned = 0

        # Clean old session logs
        cleaned = cleanup_old_session_logs()
        if cleaned > 0:
            print(f"[Progress] Cleaned {cleaned} old session log(s)", file=sys.stderr)
            total_cleaned += cleaned

        # Clean temp files (be conservative)
        cleaned = cleanup_temp_files(cwd)
        if cleaned > 0:
            print(f"[Progress] Cleaned {cleaned} temp file(s)", file=sys.stderr)
            total_cleaned += cleaned

        # Clean empty artifact directories
        cleaned = cleanup_empty_dirs(cwd)
        if cleaned > 0:
            print(
                f"[Progress] Cleaned {cleaned} empty artifact dir(s)", file=sys.stderr
            )
            total_cleaned += cleaned

        if total_cleaned > 0:
            print(
                f"[Success] Cleanup complete: {total_cleaned} item(s) removed",
                file=sys.stderr,
            )

        sys.exit(0)


if __name__ == "__main__":
    main()
```
