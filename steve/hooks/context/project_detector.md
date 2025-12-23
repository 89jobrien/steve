---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: hook
---

# Project Detector

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Project detector hook.

Auto-detects project type and injects relevant patterns/context.
Runs on UserPromptSubmit.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from hook_logging import hook_invocation

# Project detection rules: (marker_files, project_type, context)
PROJECT_DETECTORS = [
    # Next.js
    (
        ["next.config.js", "next.config.mjs", "next.config.ts"],
        "Next.js",
        "App Router patterns, Server Components, use 'use client' for client components.",
    ),
    # React (standalone)
    (
        ["vite.config.ts", "vite.config.js"],
        "Vite + React",
        "Use functional components, hooks for state, Vite for bundling.",
    ),
    # FastAPI
    (
        ["main.py"],
        "FastAPI",
        "Use Pydantic models, async endpoints, dependency injection.",
    ),
    # Django
    (
        ["manage.py", "settings.py"],
        "Django",
        "Use Django ORM, class-based views, Django REST Framework for APIs.",
    ),
    # Flask
    (
        ["app.py", "wsgi.py"],
        "Flask",
        "Use Blueprints for organization, Flask-SQLAlchemy for ORM.",
    ),
    # Express.js
    (
        ["express", "app.js"],
        "Express.js",
        "Use middleware pattern, async/await, proper error handling.",
    ),
    # Rust
    (
        ["Cargo.toml"],
        "Rust",
        "Use Result for errors, lifetimes for references, cargo for builds.",
    ),
    # Go
    (
        ["go.mod"],
        "Go",
        "Use goroutines for concurrency, interfaces for abstraction, go mod for deps.",
    ),
    # Python (generic)
    (
        ["pyproject.toml", "setup.py"],
        "Python",
        "Use type hints, dataclasses, pathlib for paths, uv for package management.",
    ),
]

# Framework-specific skills mapping
SKILL_MAPPINGS = {
    "Next.js": "~/.claude/skills/nextjs-architecture/SKILL.md",
    "React": "~/.claude/skills/react-patterns/SKILL.md",
    "Python": "~/.claude/skills/python-scripting/SKILL.md",
    "FastAPI": "~/.claude/skills/fastapi/SKILL.md",
}


def detect_project(cwd: str) -> tuple[str, str] | None:
    """Detect project type from marker files.

    Returns (project_type, context_hint) or None.
    """
    cwd_path = Path(cwd)

    for markers, project_type, context in PROJECT_DETECTORS:
        for marker in markers:
            # Check direct file
            if (cwd_path / marker).exists():
                return project_type, context

            # Check package.json dependencies
            package_json = cwd_path / "package.json"
            if package_json.exists() and marker in ["next", "react", "vue", "express"]:
                try:
                    data = json.loads(package_json.read_text())
                    deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
                    if marker in deps:
                        return project_type, context
                except (json.JSONDecodeError, OSError):
                    continue

    return None


def get_skill_content(project_type: str) -> str | None:
    """Get skill content for project type."""
    skill_path = SKILL_MAPPINGS.get(project_type)
    if not skill_path:
        return None

    path = Path(skill_path).expanduser()
    if not path.exists():
        return None

    try:
        content = path.read_text()
        # Limit to first 1500 chars to avoid overwhelming context
        return content[:1500] if len(content) > 1500 else content
    except OSError:
        return None


def main() -> None:
    with hook_invocation("project_detector") as inv:
        try:
            payload = json.load(sys.stdin)
        except json.JSONDecodeError:
            sys.exit(0)

        inv.set_payload(payload)

        if payload.get("stop_hook_active"):
            sys.exit(0)

        cwd = payload.get("cwd", ".")
        prompt = payload.get("prompt", "")

        # Only trigger for code-related prompts
        code_keywords = ["code", "implement", "create", "build", "add", "fix", "refactor", "write"]
        if not any(kw in prompt.lower() for kw in code_keywords):
            sys.exit(0)

        detection = detect_project(cwd)

        if not detection:
            sys.exit(0)

        project_type, context_hint = detection

        # Build context output
        output_parts = [f"**Detected Project:** {project_type}", f"**Quick Guide:** {context_hint}"]

        # Try to load relevant skill
        skill_content = get_skill_content(project_type)
        if skill_content:
            output_parts.append(f"\n**Framework Patterns:**\n{skill_content[:500]}...")

        # Output to stdout for context injection
        print(f"\n---\n{chr(10).join(output_parts)}\n---\n")
        print(f"[Success] Detected {project_type} project", file=sys.stderr)

        sys.exit(0)


if __name__ == "__main__":
    main()
```
