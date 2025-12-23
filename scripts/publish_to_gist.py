#!/usr/bin/env python3
"""
Publish a component to GitHub Gist.

Creates or updates a GitHub Gist with component content and updates
the component's frontmatter with the gist URL.

Usage:
    python scripts/publish_to_gist.py <component-path> [--public] [--update]

Requires GITHUB_TOKEN environment variable.
"""

import argparse
import contextlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, cast

import requests
import yaml


# Default timeout for HTTP requests (seconds)
REQUEST_TIMEOUT = 30

# Error messages
ERR_CREDENTIALS_NOT_FOUND = (
    "GITHUB_TOKEN not found. Set environment variable or git config github.token"
)


def get_github_token() -> str:
    """Get GitHub token from environment or git config."""
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        return token

    # Try git config
    with contextlib.suppress(Exception):
        result = subprocess.run(
            ["git", "config", "--get", "github.token"], check=False, capture_output=True, text=True
        )
        if result.returncode == 0:
            return result.stdout.strip()

    raise ValueError(ERR_CREDENTIALS_NOT_FOUND)


def create_gist(
    content: str, filename: str, description: str, public: bool = False
) -> dict[str, Any]:
    """Create a new GitHub Gist."""
    token = get_github_token()

    url = "https://api.github.com/gists"
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}

    data = {"description": description, "public": public, "files": {filename: {"content": content}}}

    response = requests.post(url, headers=headers, json=data, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()

    return cast("dict[str, Any]", response.json())


def update_gist(gist_id: str, content: str, filename: str, description: str) -> dict[str, Any]:
    """Update an existing GitHub Gist."""
    token = get_github_token()

    url = f"https://api.github.com/gists/{gist_id}"
    headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github.v3+json"}

    data = {"description": description, "files": {filename: {"content": content}}}

    response = requests.patch(url, headers=headers, json=data, timeout=REQUEST_TIMEOUT)
    response.raise_for_status()

    return cast("dict[str, Any]", response.json())


def get_gist_id_from_url(gist_url: str) -> str:
    """Extract Gist ID from URL."""
    # Handle both formats:
    # https://gist.github.com/username/gist_id
    # https://gist.github.com/gist_id
    parts = gist_url.rstrip("/").split("/")
    return parts[-1]


def update_registry(
    repo_root: Path, component_path: Path, gist_url: str, gist_id: str, gist_data: dict[str, Any]
) -> None:
    """Update .gist-registry.json with component information."""
    registry_path = repo_root / ".gist-registry.json"

    # Load existing registry
    if registry_path.exists():
        registry = json.loads(registry_path.read_text())
    else:
        registry = {
            "version": "1.0.0",
            "description": "Registry of components published to GitHub Gists",
            "components": {},
        }

    # Parse component metadata
    content = component_path.read_text(encoding="utf-8")
    frontmatter_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    frontmatter: dict[str, Any] = {}
    if frontmatter_match:
        with contextlib.suppress(Exception):
            frontmatter = yaml.safe_load(frontmatter_match.group(1)) or {}

    # Determine component type and domain
    relative_path = str(component_path.relative_to(repo_root / "steve"))
    path_parts = relative_path.split("/")

    component_type = "unknown"
    domain = None
    name = frontmatter.get("name", component_path.stem)

    if path_parts[0] == "agents":
        component_type = "agent"
        domain = path_parts[1] if len(path_parts) > 1 else None
    elif path_parts[0] == "skills":
        component_type = "skill"
        domain = path_parts[1] if len(path_parts) > 1 else None
    elif path_parts[0] == "commands":
        component_type = "command"
        domain = path_parts[1] if len(path_parts) > 1 else None
    elif path_parts[0] == "hooks":
        component_type = "hook"
        domain = path_parts[1] if len(path_parts) > 1 else None

    # Create component entry
    now_iso = datetime.now(timezone.utc).isoformat()
    component_entry: dict[str, Any] = {
        "name": name,
        "type": component_type,
        "domain": domain,
        "path": relative_path,
        "gist_url": gist_url,
        "gist_id": gist_id,
        "description": frontmatter.get("description", ""),
        "published_at": now_iso,
        "updated_at": now_iso,
    }

    # Add type-specific metadata
    if component_type == "agent":
        component_entry.update(
            {
                "tools": frontmatter.get("tools", ""),
                "model": frontmatter.get("model", "sonnet"),
                "color": frontmatter.get("color", ""),
            }
        )

    # Use path as key for uniqueness
    registry["components"][relative_path] = component_entry

    # Write registry
    registry_path.write_text(json.dumps(registry, indent=2, ensure_ascii=False))
    print("Registry updated: .gist-registry.json")


def main() -> int:
    """Publish component to GitHub Gist."""
    parser = argparse.ArgumentParser(description="Publish component to GitHub Gist")
    parser.add_argument("component_path", help="Path to component file")
    parser.add_argument("--public", action="store_true", help="Make gist public")
    parser.add_argument("--update", action="store_true", help="Update existing gist")

    args = parser.parse_args()

    repo_root = Path(__file__).parent.parent
    component_path = repo_root / args.component_path

    if not component_path.exists():
        print(f"Error: File not found: {component_path}")
        return 1

    content = component_path.read_text(encoding="utf-8")
    filename = component_path.name
    description = f"{component_path.parent.name}/{filename} from steve repository"

    # Check if gist_url already exists in frontmatter
    frontmatter_match = re.match(r"^---\s*\n(.*?)\n---\s*\n", content, re.DOTALL)
    gist_id = None

    if frontmatter_match and args.update:
        with contextlib.suppress(Exception):
            frontmatter = yaml.safe_load(frontmatter_match.group(1))
            gist_url = frontmatter.get("gist_url", "")
            if gist_url:
                gist_id = get_gist_id_from_url(gist_url)
                print(f"Found existing gist: {gist_url}")

    try:
        if gist_id and args.update:
            print(f"Updating gist {gist_id}...")
            gist_data = update_gist(gist_id, content, filename, description)
        else:
            print("Creating new gist...")
            gist_data = create_gist(content, filename, description, args.public)

        gist_url = gist_data["html_url"]
        gist_id = gist_data["id"]
        print(f"Gist published: {gist_url}")

        # Update component file with gist_url
        subprocess.run(
            [
                sys.executable,
                "scripts/add_metadata.py",
                str(component_path.relative_to(repo_root)),
                "--gist-url",
                gist_url,
            ],
            check=False,
            cwd=repo_root,
        )

        # Update gist registry
        update_registry(repo_root, component_path, gist_url, gist_id, gist_data)

        return 0
    except requests.exceptions.RequestException as e:
        print(f"Error: Failed to publish gist: {e}")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
