---
name: jit-context
description: JIT Context Hook for Claude Code UserPromptSubmit events.
author: Joseph OBrien
status: unpublished
updated: 2025-12-23
version: 1.0.1
tag: hook
---
# Jit Context

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# ///

"""
JIT Context Hook for Claude Code UserPromptSubmit events.

Analyzes user prompts for file patterns and keywords, then pre-loads
relevant file context using head/tail slicing and grep.
"""

from __future__ import annotations

import json
import re
import sys
from collections.abc import Iterable
from pathlib import Path


def find_candidates(root: Path, patterns: Iterable[str]) -> Iterable[Path]:
    """Find files matching glob patterns."""
    for pat in patterns:
        yield from root.rglob(pat)


def head_tail(path: Path, head_lines: int = 30, tail_lines: int = 20) -> str:
    """Get first and last N lines of a file."""
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
        lines = text.splitlines()
        total = len(lines)

        if total <= head_lines + tail_lines:
            return text

        head = "\n".join(lines[:head_lines])
        tail = "\n".join(lines[-tail_lines:])
        return f"{head}\n\n... [{total - head_lines - tail_lines} lines omitted] ...\n\n{tail}"
    except Exception:
        return ""


def grep_file(path: Path, needle: str, max_hits: int = 10) -> list[tuple[int, str]]:
    """Search for needle in file, return line numbers and content."""
    hits: list[tuple[int, str]] = []
    try:
        with path.open("r", encoding="utf-8", errors="ignore") as f:
            for i, line in enumerate(f, 1):
                if needle.lower() in line.lower():
                    hits.append((i, line.rstrip("\n")))
                    if len(hits) >= max_hits:
                        break
    except Exception:
        pass
    return hits


def extract_patterns(prompt: str) -> list[str]:
    """Extract file glob patterns from user prompt."""
    patterns: list[str] = []

    # Match explicit glob patterns like *.py, **/*.ts, src/**/*
    glob_pattern = re.compile(r"[*?[\]{}]+[.\w/]*|[\w./]+[*?[\]{}]+[\w./]*")
    for match in glob_pattern.findall(prompt):
        if match.strip():
            patterns.append(match.strip())

    # Match file extensions mentioned
    ext_pattern = re.compile(r"\.(?:py|ts|js|tsx|jsx|md|json|yaml|yml|toml|sh|sql)\b")
    for ext in ext_pattern.findall(prompt):
        patterns.append(f"*{ext}")

    return list(set(patterns))


def extract_paths(prompt: str) -> list[str]:
    """Extract explicit file/directory paths from user prompt."""
    paths: list[str] = []

    # Match paths like src/, ./config, /path/to/file.py
    path_pattern = re.compile(
        r"(?:\.?/)?(?:[\w.-]+/)+[\w.-]*|[\w.-]+\.(?:py|ts|js|md|json)"
    )
    for match in path_pattern.findall(prompt):
        if match.strip() and not match.startswith("http"):
            paths.append(match.strip())

    return list(set(paths))


def extract_keywords(prompt: str) -> list[str]:
    """Extract potential search keywords from user prompt."""
    # Common programming terms to search for
    keywords: list[str] = []

    # Look for quoted strings
    quoted = re.findall(r'["\']([^"\']+)["\']', prompt)
    keywords.extend(quoted)

    # Look for function/class names (CamelCase or snake_case)
    identifiers = re.findall(r"\b[A-Z][a-zA-Z]+\b|\b[a-z]+_[a-z_]+\b", prompt)
    keywords.extend(identifiers)

    return list(set(keywords))[:5]  # Limit to avoid too many searches


def format_context(
    matched_files: list[tuple[Path, str]],
    grep_results: list[tuple[Path, list[tuple[int, str]]]],
) -> str:
    """Format the gathered context for output."""
    parts: list[str] = []

    if matched_files:
        parts.append("# JIT Context: Relevant Files\n")
        for path, content in matched_files[:5]:  # Limit files
            parts.append(f"## {path}\n```\n{content}\n```\n")

    if grep_results:
        parts.append("# JIT Context: Keyword Matches\n")
        for path, hits in grep_results[:5]:  # Limit results
            parts.append(f"## {path}")
            for lineno, line in hits:
                parts.append(f"  L{lineno}: {line[:100]}")
            parts.append("")

    return "\n".join(parts)


def parse_hook_input() -> str | None:
    """Parse hook input from stdin, return prompt or None."""
    try:
        raw = sys.stdin.read()
        if not raw.strip():
            return None
        data = json.loads(raw)
    except (json.JSONDecodeError, Exception):
        return None

    if isinstance(data, dict):
        prompt = data.get("prompt", "") or data.get("input", "") or str(data)
    elif isinstance(data, str):
        prompt = data
    else:
        return None

    return prompt if prompt and len(prompt) >= 10 else None


def collect_pattern_matches(cwd: Path, patterns: list[str]) -> list[tuple[Path, str]]:
    """Find files matching patterns and extract head/tail."""
    results: list[tuple[Path, str]] = []
    for candidate in find_candidates(cwd, patterns):
        if len(results) >= 3:
            break
        if not candidate.is_file() or candidate.stat().st_size >= 100_000:
            continue
        content = head_tail(candidate)
        if content:
            results.append((candidate.relative_to(cwd), content))
    return results


def collect_path_matches(cwd: Path, paths: list[str]) -> list[tuple[Path, str]]:
    """Check explicit paths and extract head/tail."""
    results: list[tuple[Path, str]] = []
    for p in paths:
        path = cwd / p
        if not path.is_file() or path.stat().st_size >= 100_000:
            continue
        content = head_tail(path)
        if content:
            results.append((Path(p), content))
    return results


def collect_keyword_matches(
    cwd: Path, keywords: list[str]
) -> list[tuple[Path, list[tuple[int, str]]]]:
    """Search for keywords in common source files."""
    results: list[tuple[Path, list[tuple[int, str]]]] = []
    search_patterns = ["*.py", "*.ts", "*.js", "*.md"]
    search_files = [f for f in find_candidates(cwd, search_patterns) if f.is_file()][
        :50
    ]

    for keyword in keywords[:2]:
        for f in search_files:
            if len(results) >= 3:
                return results
            hits = grep_file(f, keyword)
            if hits:
                results.append((f.relative_to(cwd), hits))
    return results


def main() -> None:
    """Main hook entry point."""
    prompt = parse_hook_input()
    if not prompt:
        return

    cwd = Path.cwd()
    patterns = extract_patterns(prompt)
    paths = extract_paths(prompt)
    keywords = extract_keywords(prompt)

    matched_files = collect_pattern_matches(cwd, patterns)
    matched_files.extend(collect_path_matches(cwd, paths))

    grep_results: list[tuple[Path, list[tuple[int, str]]]] = []
    if keywords and not matched_files:
        grep_results = collect_keyword_matches(cwd, keywords)

    context = format_context(matched_files, grep_results)
    if context:
        print(context)


if __name__ == "__main__":
    main()
```
