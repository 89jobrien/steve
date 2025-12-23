#!/usr/bin/env python3
"""
Publish the component registry to a GitHub Gist.

Creates or updates a Gist containing the .gist-registry.json file,
making it available for remote component discovery and installation.

Usage:
    python scripts/publish_registry.py [--public] [--update]

Requires GITHUB_TOKEN environment variable.
"""

import argparse
import contextlib
import os
import subprocess
from pathlib import Path
from typing import Any, cast

import requests


# Default timeout for HTTP requests (seconds)
REQUEST_TIMEOUT = 30

# Error messages
ERR_CREDENTIALS_NOT_FOUND = (
    "GitHub token not found. "
    "Set the GITHUB_TOKEN environment variable or configure 'github.token' in git config."
)


def get_github_token() -> str:
    """Get GitHub token from environment or git config.

    Returns:
        str: The token string.

    Raises:
        RuntimeError: If a GitHub token cannot be found.
    """
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        return token

    with contextlib.suppress(Exception):
        result = subprocess.run(
            ["git", "config", "--get", "github.token"], check=False, capture_output=True, text=True
        )
        if result.returncode == 0:
            return result.stdout.strip()

    raise RuntimeError(ERR_CREDENTIALS_NOT_FOUND)


def get_existing_gist_id(repo_root: Path) -> str | None:
    """Check if registry gist URL is stored in a config file."""
    # Check for .gist-registry-url file
    url_file = repo_root / ".gist-registry-url"
    if url_file.exists():
        url = url_file.read_text().strip()
        return url.rstrip("/").split("/")[-1]
    return None


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


def main() -> int:
    """Publish component registry to GitHub Gist."""
    parser = argparse.ArgumentParser(description="Publish component registry to GitHub Gist")
    parser.add_argument("--public", action="store_true", help="Make gist public")
    parser.add_argument("--update", action="store_true", help="Update existing gist")

    args = parser.parse_args()

    repo_root = Path(__file__).parent.parent
    registry_path = repo_root / ".gist-registry.json"

    if not registry_path.exists():
        print(
            "Error: .gist-registry.json not found. Run build_index.py first or publish some components."
        )
        return 1

    registry_content = registry_path.read_text(encoding="utf-8")
    description = "steve component registry - Discover and install Claude Code components"

    gist_id = None
    if args.update:
        gist_id = get_existing_gist_id(repo_root)
        if gist_id:
            print(f"Found existing registry gist: {gist_id}")
        else:
            print("Warning: No existing registry gist found. Creating new one.")

    try:
        if gist_id and args.update:
            print(f"Updating registry gist {gist_id}...")
            gist_data = update_gist(gist_id, registry_content, "gist-registry.json", description)
        else:
            print("Creating new registry gist...")
            gist_data = create_gist(
                registry_content, "gist-registry.json", description, args.public
            )

        gist_url = gist_data["html_url"]
        print(f"Registry published: {gist_url}")

        # Save gist URL for future updates
        url_file = repo_root / ".gist-registry-url"
        url_file.write_text(gist_url)
        print("Registry URL saved to .gist-registry-url")

        print("\nTo use this registry remotely:")
        print(f"  python scripts/list_components.py --from-registry --registry-url {gist_url}")
        print(
            f"  python scripts/install_component.py <name> --from-registry --registry-url {gist_url}"
        )

        return 0
    except requests.exceptions.RequestException as e:
        print(f"Error: Failed to publish registry: {e}")
        return 1
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
