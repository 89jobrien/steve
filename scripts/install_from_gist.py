#!/usr/bin/env python3
"""
Install a component from a GitHub Gist.

Downloads a component from a Gist URL and installs it in the appropriate
location in the steve repository.

Usage:
    python scripts/install_from_gist.py <gist-url> [--target-path path]
"""

import argparse
import re
from pathlib import Path
from typing import Any

import requests
import yaml


def get_gist_id_from_url(gist_url: str) -> str:
    """Extract Gist ID from URL."""
    parts = gist_url.rstrip("/").split("/")
    return parts[-1]


def fetch_gist(gist_id: str) -> dict[str, Any]:
    """Fetch Gist content from GitHub API."""
    url = f"https://api.github.com/gists/{gist_id}"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.json()


def determine_target_path(filename: str, content: str, repo_root: Path) -> Path:
    """Determine target path based on filename and content."""
    # Parse frontmatter to determine component type
    frontmatter_pattern = r"^---\s*\n(.*?)\n---\s*\n"
    match = re.match(frontmatter_pattern, content, re.DOTALL)

    if match:
        try:
            frontmatter = yaml.safe_load(match.group(1))
            component_type = frontmatter.get("type", "")
            domain = frontmatter.get("domain", "")
        except Exception:
            frontmatter = {}
            component_type = ""
            domain = ""
    else:
        frontmatter = {}
        component_type = ""
        domain = ""

    steve_dir = repo_root / "steve"

    # Determine path based on filename patterns
    if filename.startswith("SKILL.md") or "skill" in filename.lower():
        skill_name = frontmatter.get("name", filename.replace(".md", ""))
        return steve_dir / "skills" / skill_name / "SKILL.md"
    if "agent" in filename.lower() or component_type == "agent":
        domain_dir = domain or "core"
        return steve_dir / "agents" / domain_dir / filename
    if "command" in filename.lower() or component_type == "command":
        category = "util"  # Default category
        return steve_dir / "commands" / category / filename
    if "hook" in filename.lower() or component_type == "hook":
        hook_type = "workflows"  # Default hook type
        return steve_dir / "hooks" / hook_type / filename
    # Default to agents/core
    return steve_dir / "agents" / "core" / filename


def main() -> int:
    parser = argparse.ArgumentParser(description="Install component from GitHub Gist")
    parser.add_argument("gist_url", help="GitHub Gist URL")
    parser.add_argument("--target-path", help="Target path (auto-detected if not specified)")

    args = parser.parse_args()

    repo_root = Path(__file__).parent.parent

    try:
        gist_id = get_gist_id_from_url(args.gist_url)
        print(f"Fetching gist {gist_id}...")

        gist_data = fetch_gist(gist_id)

        # Get the first file from the gist
        files = gist_data.get("files", {})
        if not files:
            print("Error: Gist has no files")
            return 1

        filename = next(iter(files.keys()))
        file_data = files[filename]
        content = file_data.get("content", "")

        if not content:
            print("Error: Gist file is empty")
            return 1

        # Determine target path
        if args.target_path:
            target_path = repo_root / args.target_path
        else:
            target_path = determine_target_path(filename, content, repo_root)

        # Create parent directory if needed
        target_path.parent.mkdir(parents=True, exist_ok=True)

        # Write file
        target_path.write_text(content, encoding="utf-8")

        print(f"✓ Installed: {target_path}")
        print(f"  From: {args.gist_url}")

        return 0
    except requests.exceptions.RequestException as e:
        print(f"Error: Failed to fetch gist: {e}")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
