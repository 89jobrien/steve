---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: hook
---

# Context Injector

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///

"""
Inject relevant context based on keywords in prompt.

This hook automatically appends relevant docs/patterns based on prompt content.
Runs on UserPromptSubmit event.
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from hook_logging import hook_invocation

# Context mappings: keyword patterns -> context files/content
CONTEXT_MAPPINGS = [
    {
        "patterns": [r"\btest(s|ing)?\b", r"\bpytest\b", r"\bjest\b", r"\bvitest\b"],
        "context_file": "~/.claude/skills/testing/SKILL.md",
        "fallback": "When writing tests: use AAA pattern (Arrange, Act, Assert), mock external dependencies, aim for high coverage of edge cases.",
    },
    {
        "patterns": [r"\bdocker\b", r"\bcontainer(s|ize)?\b", r"\bDockerfile\b"],
        "context_file": "~/.claude/skills/docker/SKILL.md",
        "fallback": "Docker best practices: use multi-stage builds, minimize layers, don't run as root, use .dockerignore.",
    },
    {
        "patterns": [
            r"\bgit\b",
            r"\bcommit\b",
            r"\bpr\b",
            r"\bpull request\b",
            r"\bmerge\b",
        ],
        "context_file": "~/.claude/skills/git-workflow/SKILL.md",
        "fallback": "Git conventions: use conventional commits, keep commits atomic, write descriptive PR descriptions.",
    },
    {
        "patterns": [r"\bapi\b", r"\brest\b", r"\bendpoint(s)?\b", r"\broute(s)?\b"],
        "context_file": "~/.claude/skills/api-design/SKILL.md",
        "fallback": "API design: use proper HTTP methods, return appropriate status codes, version your APIs, validate inputs.",
    },
    {
        "patterns": [
            r"\bsecurity\b",
            r"\bauth(entication)?\b",
            r"\bauthoriz(e|ation)\b",
            r"\boauth\b",
        ],
        "context_file": "~/.claude/skills/security-audit/SKILL.md",
        "fallback": "Security: validate all inputs, use parameterized queries, implement rate limiting, follow OWASP guidelines.",
    },
    {
        "patterns": [
            r"\bperformance\b",
            r"\boptimiz(e|ation)\b",
            r"\bslow\b",
            r"\bbottleneck\b",
        ],
        "context_file": "~/.claude/skills/performance/SKILL.md",
        "fallback": "Performance: profile before optimizing, use caching strategically, optimize database queries, lazy load where appropriate.",
    },
    {
        "patterns": [
            r"\bdatabase\b",
            r"\b db \b",
            r"\bsql\b",
            r"\bquery\b",
            r"\bschema\b",
            r"\bmigration\b",
        ],
        "context_file": "~/.claude/skills/database-optimization/SKILL.md",
        "fallback": "Database: use indexes wisely, avoid N+1 queries, use transactions appropriately, normalize where sensible.",
    },
    {
        "patterns": [
            r"\breact\b",
            r"\bcomponent(s)?\b",
            r"\bhook(s)?\b",
            r"\buseState\b",
            r"\buseEffect\b",
        ],
        "context_file": "~/.claude/skills/react/SKILL.md",
        "fallback": "React: use functional components, follow hooks rules, memoize expensive computations, use proper key props.",
    },
]


def load_context_file(file_path: str) -> str | None:
    """Load context from a file if it exists."""
    path = Path(file_path).expanduser()
    if path.exists():
        try:
            content = path.read_text()
            # Return first 2000 chars to avoid overwhelming context
            return content[:2000] if len(content) > 2000 else content
        except (OSError, UnicodeDecodeError):
            pass
    return None


def find_matching_contexts(prompt: str) -> list[str]:
    """Find all contexts matching the prompt."""
    contexts = []
    prompt_lower = prompt.lower()

    for mapping in CONTEXT_MAPPINGS:
        for pattern in mapping["patterns"]:
            if re.search(pattern, prompt_lower):
                # Try to load context file
                context = load_context_file(mapping["context_file"])
                if not context:
                    context = mapping["fallback"]

                contexts.append(context)
                break  # Only add each context once

    return contexts


def main() -> None:
    with hook_invocation("context_injector") as inv:
        try:
            payload = json.load(sys.stdin)
        except json.JSONDecodeError:
            sys.exit(0)

        inv.set_payload(payload)

        prompt = payload.get("prompt", "")

        if not prompt:
            sys.exit(0)

        matching_contexts = find_matching_contexts(prompt)

        if not matching_contexts:
            sys.exit(0)

        # Output context to be injected (via stdout for UserPromptSubmit)
        # The hook system will append this to the prompt
        print("\n\n---\n**Relevant Context:**\n")
        for _, context in enumerate(matching_contexts[:3], 1):  # Limit to 3 contexts
            print(f"\n{context}\n")

        sys.exit(0)


if __name__ == "__main__":
    main()
```
