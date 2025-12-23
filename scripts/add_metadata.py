#!/usr/bin/env python3
"""
Add or update metadata in component files.

Adds gist_url and other metadata to component frontmatter.

Usage:
    python scripts/add_metadata.py <component-path> [--gist-url URL] [--key value]
"""

import argparse
import re
from pathlib import Path
from typing import Any

import yaml


def parse_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    """Extract YAML frontmatter from markdown content."""
    frontmatter_pattern = r"^---\s*\n(.*?)\n---\s*\n(.*)$"
    match = re.match(frontmatter_pattern, content, re.DOTALL)

    if match:
        frontmatter_str = match.group(1)
        body = match.group(2)
        try:
            frontmatter = yaml.safe_load(frontmatter_str) or {}
            return frontmatter, body
        except yaml.YAMLError:
            return {}, content
    return {}, content


def update_frontmatter(content: str, updates: dict[str, Any]) -> str:
    """Update frontmatter with new values."""
    frontmatter, body = parse_frontmatter(content)

    # Update frontmatter
    frontmatter.update(updates)

    # Reconstruct file
    frontmatter_yaml = yaml.dump(frontmatter, default_flow_style=False, sort_keys=False)
    return f"---\n{frontmatter_yaml}---\n\n{body}"


def main() -> int:
    """Add metadata to component frontmatter."""
    parser = argparse.ArgumentParser(description="Add metadata to component files")
    parser.add_argument("component_path", help="Path to component file")
    parser.add_argument("--gist-url", help="Gist URL for the component")
    parser.add_argument(
        "--key",
        action="append",
        nargs=2,
        metavar=("KEY", "VALUE"),
        help="Add custom key-value pair (can be used multiple times)",
    )

    args = parser.parse_args()

    repo_root = Path(__file__).parent.parent
    component_path = repo_root / args.component_path

    if not component_path.exists():
        print(f"Error: File not found: {component_path}")
        return 1

    content = component_path.read_text(encoding="utf-8")
    updates = {}

    if args.gist_url:
        updates["gist_url"] = args.gist_url

    if args.key:
        updates.update(dict(args.key))

    if not updates:
        print("Error: No updates specified")
        return 1

    updated_content = update_frontmatter(content, updates)
    component_path.write_text(updated_content, encoding="utf-8")

    print(f"✓ Updated {component_path}")
    for key, value in updates.items():
        print(f"  {key}: {value}")

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
