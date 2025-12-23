---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: hook
---

# Commit Suggester

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Commit suggester hook.

Generates commit message suggestion based on session changes.
Runs on Stop event.
"""

from __future__ import annotations

import asyncio
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from hook_logging import hook_invocation

SUGGESTIONS_DIR = Path.home() / ".claude" / "commit-suggestions"


def command_exists(cmd: str) -> bool:
    """Check if command exists."""
    return shutil.which(cmd) is not None


async def get_staged_changes(cwd: str) -> tuple[str, list[str]]:
    """Get staged changes diff and file list."""
    if not command_exists("git"):
        return "", []

    try:
        # Get staged files
        proc = await asyncio.create_subprocess_exec(
            "git",
            "diff",
            "--cached",
            "--name-only",
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=10)
        staged_files = [f for f in stdout.decode().strip().splitlines() if f]

        if not staged_files:
            # Check unstaged changes
            proc = await asyncio.create_subprocess_exec(
                "git",
                "diff",
                "--name-only",
                cwd=cwd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=10)
            staged_files = [f for f in stdout.decode().strip().splitlines() if f]

        if not staged_files:
            return "", []

        # Get diff stat
        proc = await asyncio.create_subprocess_exec(
            "git",
            "diff",
            "--stat",
            cwd=cwd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, _ = await asyncio.wait_for(proc.communicate(), timeout=10)
        diff_stat = stdout.decode().strip()

        return diff_stat, staged_files

    except (asyncio.TimeoutError, OSError):
        return "", []


def generate_commit_message(files: list[str], diff_stat: str) -> str:
    """Generate a commit message based on changed files."""
    if not files:
        return ""

    # Categorize files
    categories = {
        "feat": [],
        "fix": [],
        "docs": [],
        "test": [],
        "refactor": [],
        "style": [],
        "chore": [],
    }

    for f in files:
        f_lower = f.lower()
        if "test" in f_lower or "spec" in f_lower:
            categories["test"].append(f)
        elif f_lower.endswith(".md") or "doc" in f_lower:
            categories["docs"].append(f)
        elif "fix" in f_lower or "bug" in f_lower:
            categories["fix"].append(f)
        elif any(cfg in f_lower for cfg in ["config", ".json", ".yaml", ".toml", "package"]):
            categories["chore"].append(f)
        elif any(style in f_lower for style in [".css", ".scss", ".less", "style"]):
            categories["style"].append(f)
        else:
            categories["feat"].append(f)

    # Determine primary type
    primary_type = "feat"
    max_count = 0
    for cat_type, cat_files in categories.items():
        if len(cat_files) > max_count:
            max_count = len(cat_files)
            primary_type = cat_type

    # Generate message
    primary_files = categories[primary_type]
    if len(primary_files) == 1:
        scope = Path(primary_files[0]).stem
        return f"{primary_type}({scope}): update {Path(primary_files[0]).name}"
    elif len(primary_files) <= 3:
        return f"{primary_type}: update {', '.join(Path(f).name for f in primary_files[:3])}"
    else:
        # Find common directory
        dirs = [str(Path(f).parent) for f in primary_files]
        common = Path(dirs[0]).parts[0] if dirs else "project"
        return f"{primary_type}({common}): update {len(primary_files)} files"


def save_suggestion(cwd: str, message: str, files: list[str], diff_stat: str) -> Path:
    """Save commit suggestion to file."""
    SUGGESTIONS_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    suggestion_file = SUGGESTIONS_DIR / f"commit_{timestamp}.md"

    content = f"""# Commit Suggestion

**Generated:** {datetime.now().isoformat()}
**Directory:** {cwd}

## Suggested Message

```

{message}

```

## Changed Files

{chr(10).join(f'- {f}' for f in files)}

## Diff Stats

```

{diff_stat}

```

## Usage

```bash
git add -A
git commit -m "{message}"
```

"""

    suggestion_file.write_text(content)
    return suggestion_file

def main() -> None:
    with hook_invocation("commit_suggester") as inv:
        try:
            payload = json.load(sys.stdin)
        except json.JSONDecodeError:
            sys.exit(0)

        inv.set_payload(payload)

        cwd = payload.get("cwd", ".")

        # Get changes
        diff_stat, files = asyncio.run(get_staged_changes(cwd))

        if not files:
            sys.exit(0)

        # Generate suggestion
        message = generate_commit_message(files, diff_stat)

        if not message:
            sys.exit(0)

        # Save suggestion
        suggestion_file = save_suggestion(cwd, message, files, diff_stat)

        # Output suggestion
        print("\n" + "=" * 50, file=sys.stderr)
        print("[Success] Commit suggestion generated:", file=sys.stderr)
        print(f"\n  {message}\n", file=sys.stderr)
        print(f"  Files changed: {len(files)}", file=sys.stderr)
        print(f"  Saved to: {suggestion_file}", file=sys.stderr)
        print("=" * 50 + "\n", file=sys.stderr)

        sys.exit(0)

if __name__ == "__main__":
    main()

```
