#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml"]
# ///

"""
Just-In-Time Context Hook for Claude Code UserPromptSubmit events.

Provides token-controlled context injection with configurable limits.
Extracts snippets around matches instead of full file dumps.
"""

from __future__ import annotations

import json
import re
import sys
from collections.abc import Iterable
from pathlib import Path


def estimate_tokens(text: str) -> int:
    """Rough token estimation: ~4 characters per token."""
    return len(text) // 4


def load_config() -> dict:
    """Load jit_context configuration from hooks_config.yaml."""
    try:
        import yaml

        config_path = Path(__file__).parent.parent / "hooks_config.yaml"
        if not config_path.exists():
            return get_default_config()

        with config_path.open() as f:
            config = yaml.safe_load(f) or {}
            jit_config = config.get("context", {}).get("jit_context", {})

            # Merge with defaults
            defaults = get_default_config()
            return {**defaults, **jit_config}
    except Exception:
        return get_default_config()


def get_default_config() -> dict:
    """Default configuration if no config file exists."""
    return {
        "enabled": True,
        "max_tokens": 500,  # Maximum total tokens for all context
        "max_files": 3,  # Maximum files to include
        "max_file_size_kb": 50,  # Skip files larger than this
        "context_lines": 3,  # Lines before/after matches
        "max_matches_per_file": 3,  # Max matches to show per file
        "snippet_chars": 200,  # Max characters per snippet
    }


class TokenBudget:
    """Tracks token usage and enforces budget."""

    def __init__(self, max_tokens: int):
        self.max_tokens = max_tokens
        self.used_tokens = 0

    def can_add(self, text: str) -> bool:
        """Check if text fits in remaining budget."""
        tokens = estimate_tokens(text)
        return self.used_tokens + tokens <= self.max_tokens

    def add(self, text: str) -> bool:
        """Add text if it fits in budget. Returns True if added."""
        tokens = estimate_tokens(text)
        if self.used_tokens + tokens <= self.max_tokens:
            self.used_tokens += tokens
            return True
        return False

    @property
    def remaining(self) -> int:
        """Get remaining token budget."""
        return max(0, self.max_tokens - self.used_tokens)


def extract_snippet(
    lines: list[str], match_idx: int, context_lines: int, max_chars: int
) -> str:
    """Extract snippet around a match with context lines."""
    start = max(0, match_idx - context_lines)
    end = min(len(lines), match_idx + context_lines + 1)
    snippet_lines = lines[start:end]

    # Truncate if too long
    snippet = "\n".join(snippet_lines)
    if len(snippet) > max_chars:
        snippet = snippet[:max_chars] + "..."

    return snippet


def find_in_file(
    path: Path,
    search_term: str,
    config: dict,
    budget: TokenBudget,
) -> list[tuple[int, str]]:
    """Search for term in file, return snippets with line numbers."""
    try:
        if path.stat().st_size > config["max_file_size_kb"] * 1024:
            return []

        text = path.read_text(encoding="utf-8", errors="ignore")
        lines = text.splitlines()
        matches: list[tuple[int, str]] = []

        for i, line in enumerate(lines):
            if search_term.lower() in line.lower():
                snippet = extract_snippet(
                    lines, i, config["context_lines"], config["snippet_chars"]
                )

                # Check if snippet fits in budget
                formatted = f"L{i+1}: {snippet}"
                if not budget.can_add(formatted):
                    break

                matches.append((i + 1, snippet))
                if len(matches) >= config["max_matches_per_file"]:
                    break

        return matches
    except Exception:
        return []


def find_files(root: Path, patterns: Iterable[str], max_files: int) -> list[Path]:
    """Find files matching patterns, limited to max_files."""
    found: list[Path] = []
    seen = set()

    for pat in patterns:
        for path in root.rglob(pat):
            if path in seen:
                continue
            if path.is_file():
                found.append(path)
                seen.add(path)
                if len(found) >= max_files:
                    return found

    return found


def extract_patterns(prompt: str) -> list[str]:
    """Extract file glob patterns from user prompt."""
    patterns: list[str] = []

    # Match explicit glob patterns like *.py, **/*.ts, src/**/*
    glob_pattern = re.compile(r"[*?[\]{}]+[.\w/]*|[\w./]+[*?[\]{}]+[\w./]*")
    for match in glob_pattern.findall(prompt):
        if match.strip():
            patterns.append(match.strip())

    # Match file extensions mentioned
    ext_pattern = re.compile(
        r"\.(?:py|ts|js|tsx|jsx|md|json|yaml|yml|toml|sh|sql|rs|go|java)\b"
    )
    for ext in ext_pattern.findall(prompt):
        patterns.append(f"*{ext}")

    return list(set(patterns))


def extract_paths(prompt: str, cwd: Path) -> list[Path]:
    """Extract explicit file/directory paths from user prompt."""
    paths: list[Path] = []

    # Match paths like src/, ./config, /path/to/file.py
    path_pattern = re.compile(
        r"(?:\.?/)?(?:[\w.-]+/)+[\w.-]*|[\w.-]+\.(?:py|ts|js|md|json|rs|go|java)"
    )
    for match in path_pattern.findall(prompt):
        if match.strip() and not match.startswith("http"):
            path = cwd / match.strip()
            if path.exists() and path.is_file():
                paths.append(path)

    return paths


def extract_keywords(prompt: str) -> list[str]:
    """Extract potential search keywords from user prompt."""
    keywords: list[str] = []

    # Look for quoted strings
    quoted = re.findall(r'["\']([^"\']{3,})["\']', prompt)
    keywords.extend(quoted)

    # Look for function/class names (CamelCase or snake_case)
    identifiers = re.findall(r"\b[A-Z][a-zA-Z]{2,}\b|\b[a-z]+_[a-z_]+\b", prompt)
    keywords.extend(identifiers)

    return list(set(keywords))[:2]  # Limit to 2 keywords


def add_explicit_file(
    path: Path, cwd: Path, budget: TokenBudget, parts: list[str]
) -> bool:
    """Add explicit file to context. Returns True if added successfully."""
    try:
        rel_path = path.relative_to(cwd)
    except ValueError:
        rel_path = path

    header = f"\n## {rel_path}"
    if not budget.can_add(header):
        return False

    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
        lines = text.splitlines()[:10]
        snippet = "\n".join(lines)

        if len(lines) < len(text.splitlines()):
            snippet += f"\n... ({len(text.splitlines()) - 10} more lines)"

        if budget.can_add(header + "\n" + snippet):
            parts.append(header)
            parts.append(snippet)
            return True
    except Exception:
        pass

    return False


def add_keyword_matches(
    path: Path, cwd: Path, keyword: str, config: dict, budget: TokenBudget, parts: list[str]
) -> bool:
    """Add keyword matches for a file. Returns True if added successfully."""
    matches = find_in_file(path, keyword, config, budget)
    if not matches:
        return False

    try:
        rel_path = path.relative_to(cwd)
    except ValueError:
        rel_path = path

    header = f"\n## {rel_path} (matched: '{keyword}')"
    if not budget.can_add(header):
        return False

    parts.append(header)
    for line_num, snippet in matches:
        line_text = f"L{line_num}: {snippet}"
        if budget.add(line_text):
            parts.append(line_text)

    return True


def build_context(
    cwd: Path,
    explicit_paths: list[Path],
    pattern_files: list[Path],
    keywords: list[str],
    config: dict,
) -> str:
    """Build context output within token budget."""
    budget = TokenBudget(config["max_tokens"])
    parts: list[str] = []
    files_included = 0
    max_files = config["max_files"]

    # Priority 1: Explicit paths mentioned in prompt
    for path in explicit_paths[:max_files]:
        if files_included >= max_files:
            break
        if add_explicit_file(path, cwd, budget, parts):
            files_included += 1

    # Priority 2: Search in pattern-matched files for keywords
    if keywords and files_included < max_files:
        search_files = pattern_files[:10]
        for keyword in keywords:
            if files_included >= max_files:
                break
            for path in search_files:
                if files_included >= max_files:
                    break
                if add_keyword_matches(path, cwd, keyword, config, budget, parts):
                    files_included += 1

    # Add metadata footer
    if parts:
        footer = f"\n---\n*JIT Context: {files_included} files, ~{budget.used_tokens} tokens*"
        parts.append(footer)

    return "\n".join(parts) if parts else ""


def parse_hook_input() -> tuple[str, Path] | None:
    """Parse hook input from stdin, return (prompt, cwd) or None."""
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return None
        data = json.loads(raw)
    except (json.JSONDecodeError, Exception):
        return None

    if isinstance(data, dict):
        prompt = data.get("prompt", "") or data.get("input", "")
        cwd = Path(data.get("cwd", "."))
    elif isinstance(data, str):
        prompt = data
        cwd = Path.cwd()
    else:
        return None

    return (prompt, cwd) if prompt and len(prompt) >= 10 else None


def main() -> None:
    """Main hook entry point."""
    config = load_config()

    if not config.get("enabled", True):
        return

    parsed = parse_hook_input()
    if not parsed:
        return

    prompt, cwd = parsed

    # Extract search targets from prompt
    patterns = extract_patterns(prompt)
    explicit_paths = extract_paths(prompt, cwd)
    keywords = extract_keywords(prompt)

    # Skip if nothing to search for
    if not patterns and not explicit_paths and not keywords:
        return

    # Find files matching patterns
    pattern_files = find_files(cwd, patterns, config["max_files"] * 3)

    # Build context within token budget
    context = build_context(cwd, explicit_paths, pattern_files, keywords, config)

    if context:
        # Output as JSON for proper hook protocol
        output = {
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": context,
            }
        }
        print(json.dumps(output))


if __name__ == "__main__":
    main()
