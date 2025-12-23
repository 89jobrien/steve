---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: hook
---

# Related Files

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Related files hook.

Finds and injects related files based on prompt topic.
Runs on UserPromptSubmit.
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from hook_logging import hook_invocation

# Maximum files to suggest
MAX_SUGGESTIONS = 5

# File patterns to search for based on keywords
KEYWORD_FILE_PATTERNS = {
    # Testing
    r"\btest(s|ing)?\b": ["**/test_*.py", "**/*.test.ts", "**/*.spec.ts", "**/tests/**"],
    r"\bpytest\b": ["**/test_*.py", "**/conftest.py", "pytest.ini", "pyproject.toml"],
    r"\bjest\b": ["**/*.test.ts", "**/*.spec.ts", "jest.config.*"],
    # Configuration
    r"\bconfig(uration)?\b": ["**/config.*", "**/*.config.*", ".env*", "settings.*"],
    r"\benv(ironment)?\b": [".env*", "**/*.env", "**/env.*"],
    # Database
    r"\bdatabase\b|\bdb\b|\bmigration": ["**/models.*", "**/migrations/**", "**/schema.*", "alembic.ini"],
    r"\bsql\b": ["**/*.sql", "**/queries/**"],
    # API
    r"\bapi\b|\bendpoint|\broute": ["**/routes/**", "**/api/**", "**/endpoints/**", "**/views.*"],
    r"\brest\b|\bopenapi\b|\bswagger": ["**/openapi.*", "**/swagger.*", "**/api/**"],
    # Auth
    r"\bauth(entication|orization)?\b": ["**/auth/**", "**/middleware/**", "**/security/**"],
    # Components (frontend)
    r"\bcomponent": ["**/components/**", "**/*.tsx", "**/*.vue"],
    r"\bhook": ["**/hooks/**", "**/use*.ts"],
    # Styles
    r"\bstyle|\bcss|\bsass": ["**/*.css", "**/*.scss", "**/*.sass", "**/styles/**"],
    # Documentation
    r"\bdoc(s|umentation)?\b|\breadme": ["README*", "CHANGELOG*", "docs/**", "**/*.md"],
}


def find_matching_files(cwd: str, prompt: str) -> list[Path]:
    """Find files matching keywords in prompt."""
    cwd_path = Path(cwd)
    matching_files: set[Path] = set()

    prompt_lower = prompt.lower()

    for keyword_pattern, file_patterns in KEYWORD_FILE_PATTERNS.items():
        if re.search(keyword_pattern, prompt_lower):
            for pattern in file_patterns:
                try:
                    for match in cwd_path.glob(pattern):
                        if match.is_file() and not any(
                            p in str(match) for p in ["node_modules", "__pycache__", ".git", "dist", "build"]
                        ):
                            matching_files.add(match)
                except OSError:
                    continue

    return sorted(matching_files, key=lambda p: p.stat().st_mtime if p.exists() else 0, reverse=True)[:MAX_SUGGESTIONS]


def extract_file_mentions(prompt: str) -> list[str]:
    """Extract explicit file mentions from prompt."""
    # Match common file patterns
    patterns = [
        r"\b([a-zA-Z_][\w/.-]*\.(py|ts|tsx|js|jsx|json|yaml|yml|md|sql|css|scss))\b",
        r"['\"]([^'\"]+\.(py|ts|tsx|js|jsx|json|yaml|yml|md|sql|css|scss))['\"]",
    ]

    mentions = set()
    for pattern in patterns:
        for match in re.finditer(pattern, prompt):
            mentions.add(match.group(1))

    return list(mentions)


def main() -> None:
    with hook_invocation("related_files") as inv:
        try:
            payload = json.load(sys.stdin)
        except json.JSONDecodeError:
            sys.exit(0)

        inv.set_payload(payload)

        if payload.get("stop_hook_active"):
            sys.exit(0)

        prompt = payload.get("prompt", "")
        cwd = payload.get("cwd", ".")

        if not prompt or len(prompt) < 10:
            sys.exit(0)

        # Find keyword-based matches
        keyword_matches = find_matching_files(cwd, prompt)

        # Find explicit file mentions
        file_mentions = extract_file_mentions(prompt)

        if not keyword_matches and not file_mentions:
            sys.exit(0)

        output_parts = []

        if keyword_matches:
            files_list = "\n".join(f"- `{f.relative_to(cwd)}`" for f in keyword_matches[:MAX_SUGGESTIONS])
            output_parts.append(f"**Related Files Found:**\n{files_list}")

        if file_mentions:
            mentions_list = "\n".join(f"- `{f}`" for f in file_mentions[:MAX_SUGGESTIONS])
            output_parts.append(f"**Files Mentioned:**\n{mentions_list}")

        if output_parts:
            print(f"\n---\n{chr(10).join(output_parts)}\n---\n")
            print(f"[Success] Found {len(keyword_matches)} related files", file=sys.stderr)

        sys.exit(0)


if __name__ == "__main__":
    main()
```
