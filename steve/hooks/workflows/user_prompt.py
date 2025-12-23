#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml"]
# ///
"""UserPromptSubmit workflow - injects context when user submits a prompt.

This workflow runs context providers that add relevant information
to the conversation via stdout.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any


# Add hooks root to path
HOOKS_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(HOOKS_ROOT))

from hook_logging import hook_invocation  # noqa: E402


def load_config() -> dict[str, Any]:
    """Load hooks configuration."""
    config_path = HOOKS_ROOT / "hooks_config.yaml"
    if not config_path.exists():
        return {}
    try:
        import yaml

        with config_path.open() as f:
            return yaml.safe_load(f) or {}
    except Exception:
        return {}


def is_enabled(check_name: str, config: dict) -> bool:
    """Check if a context provider is enabled."""
    context_config = config.get("context", {})
    check_config = context_config.get(check_name, {})
    if isinstance(check_config, dict):
        return check_config.get("enabled", True)
    return True


def detect_project_type(cwd: str) -> str | None:
    """Detect project type and return hint."""
    cwd_path = Path(cwd)

    # Next.js
    for marker in ["next.config.js", "next.config.mjs", "next.config.ts"]:
        if (cwd_path / marker).exists():
            return "Next.js: use App Router patterns, Server Components, and API routes"

    # FastAPI
    if (cwd_path / "main.py").exists():
        try:
            content = (cwd_path / "main.py").read_text()
            if "fastapi" in content.lower():
                return "FastAPI: use Pydantic models, async endpoints, dependency injection"
        except Exception:
            pass

    # Django
    if (cwd_path / "manage.py").exists():
        return "Django: use Models, Views, Templates, and ORM patterns"

    # React (without Next.js)
    for marker in ["src/App.jsx", "src/App.tsx"]:
        if (cwd_path / marker).exists():
            return "React: use functional components, follow hooks rules, memoize expensive computations, use proper key props"

    # Python project
    if (cwd_path / "pyproject.toml").exists():
        return "Python: use type hints, async where appropriate, follow PEP standards"

    # TypeScript project
    if (cwd_path / "tsconfig.json").exists():
        return "TypeScript: use strict types, avoid any, prefer interfaces"

    return None


def get_recent_changes(cwd: str) -> str | None:
    """Get recent git changes if relevant."""
    try:
        result = subprocess.run(
            ["git", "diff", "--stat", "HEAD~3", "--", "."],
            check=False,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0 and result.stdout.strip():
            lines = result.stdout.strip().split("\n")
            if len(lines) > 1:
                return f"Recent changes:\n{chr(10).join(lines[:5])}"
    except Exception:
        pass
    return None


def find_related_files(prompt: str, cwd: str) -> list[str]:
    """Find files that might be related to the prompt."""
    related = []
    cwd_path = Path(cwd)

    # Extract potential file/module names from prompt
    words = prompt.lower().split()
    keywords = [w for w in words if len(w) > 3 and w.isalnum()]

    # Look for matching files
    for keyword in keywords[:3]:  # Limit search
        try:
            for ext in ["py", "ts", "tsx", "js", "jsx"]:
                matches = list(cwd_path.glob(f"**/*{keyword}*.{ext}"))[:2]
                related.extend(str(m.relative_to(cwd_path)) for m in matches)
        except Exception:
            continue

    return related[:5]  # Limit results


def run_context_providers(payload: dict[str, Any], config: dict) -> list[str]:
    """Run context providers and collect output."""
    context_parts: list[str] = []
    cwd = payload.get("cwd", ".")
    prompt = payload.get("prompt", "")

    # Project detection
    if is_enabled("project_detector", config):
        hint = detect_project_type(cwd)
        if hint:
            context_parts.append(hint)

    # Recent changes (only if prompt mentions certain keywords)
    if is_enabled("recent_changes", config):
        trigger_words = ["recent", "changed", "diff", "history", "last"]
        if any(word in prompt.lower() for word in trigger_words):
            changes = get_recent_changes(cwd)
            if changes:
                context_parts.append(changes)

    # Related files
    if is_enabled("related_files", config) and len(prompt) > 20:
        related = find_related_files(prompt, cwd)
        if related:
            context_parts.append(f"Possibly related files: {', '.join(related)}")

    return context_parts


def build_json_output(
    additional_context: str | None = None,
    decision: str | None = None,
    reason: str | None = None,
) -> dict:
    """Build proper JSON output per Claude Code hooks spec."""
    output: dict = {}

    if decision:
        output["decision"] = decision
        if reason:
            output["reason"] = reason

    if additional_context:
        output["hookSpecificOutput"] = {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": additional_context,
        }

    return output


def main() -> None:
    with hook_invocation("user_prompt_workflow") as inv:
        try:
            payload = json.load(sys.stdin)
        except json.JSONDecodeError:
            sys.exit(0)

        inv.set_payload(payload)

        if payload.get("stop_hook_active"):
            sys.exit(0)

        config = load_config()
        context_parts = run_context_providers(payload, config)

        # Output context via JSON (proper format per docs)
        if context_parts:
            context = "**Relevant Context:**\n" + "\n".join(context_parts)
            output = build_json_output(additional_context=context)
            print(json.dumps(output))

        sys.exit(0)


if __name__ == "__main__":
    main()
