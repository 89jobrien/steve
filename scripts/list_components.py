#!/usr/bin/env python3
"""
List available components from the gist registry or local repository.

Usage:
    python scripts/list_components.py [--type TYPE] [--domain DOMAIN] [--search QUERY]
    python scripts/list_components.py --from-registry [--registry-url URL]
"""

import argparse
import json
from pathlib import Path
from typing import Any

import requests


def load_local_registry(repo_root: Path) -> dict[str, Any]:
    """Load local gist registry."""
    registry_path = repo_root / ".gist-registry.json"
    try:
        if registry_path.exists():
            return json.loads(registry_path.read_text())
        elif not registry_path.exists():
            return repo_root / "index.json"
        return {"components": {}}
    except Exception as e:
        print(f"Error: {e}")


def load_remote_registry(registry_url: str) -> dict[str, Any]:
    """Load registry from a remote Gist."""
    gist_id = registry_url.rstrip("/").split("/")[-1]
    url = f"https://api.github.com/gists/{gist_id}"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    gist_data = response.json()

    # Find the registry file
    for filename, file_data in gist_data.get("files", {}).items():
        if filename.endswith(".json"):
            return json.loads(file_data.get("content", "{}"))

    return {"components": {}}


def filter_components(
    components: dict[str, Any],
    component_type: str | None = None,
    domain: str | None = None,
    search: str | None = None,
) -> list[dict[str, Any]]:
    """Filter components by type, domain, or search query."""
    filtered = []

    for path, component in components.items():
        # Filter by type
        if component_type and component.get("type") != component_type:
            continue

        # Filter by domain
        if domain and component.get("domain") != domain:
            continue

        # Filter by search query
        if search:
            query_lower = search.lower()
            name = component.get("name", "").lower()
            description = component.get("description", "").lower()
            path_lower = path.lower()

            if (
                query_lower not in name
                and query_lower not in description
                and query_lower not in path_lower
            ):
                continue

        filtered.append(component)

    return sorted(filtered, key=lambda x: x.get("name", ""))


def print_components(components: list[dict[str, Any]], show_details: bool = False):
    """Print components in a formatted list."""
    if not components:
        print("No components found.")
        return

    print(f"\nFound {len(components)} component(s):\n")

    for component in components:
        name = component.get("name", "unknown")
        component_type = component.get("type", "unknown")
        domain = component.get("domain", "")
        description = component.get("description", "")
        gist_url = component.get("gist_url", "")

        print(f"  {name} ({component_type})")
        if domain:
            print(f"    Domain: {domain}")
        if description:
            print(f"    {description[:80]}{'...' if len(description) > 80 else ''}")
        if gist_url:
            print(f"    Gist: {gist_url}")

        if show_details:
            path = component.get("path", "")
            if path:
                print(f"    Path: {path}")
            published = component.get("published_at", "")
            if published:
                print(f"    Published: {published}")

        print()


def main() -> int:
    parser = argparse.ArgumentParser(description="List available components")
    parser.add_argument(
        "--type", choices=["agent", "command", "skill", "hook"], help="Filter by component type"
    )
    parser.add_argument("--domain", help="Filter by domain/category")
    parser.add_argument("--search", help="Search in name, description, or path")
    parser.add_argument(
        "--from-registry", action="store_true", help="Load from remote registry Gist"
    )
    parser.add_argument("--registry-url", help="URL of registry Gist (default: from local config)")
    parser.add_argument("--details", action="store_true", help="Show detailed information")

    args = parser.parse_args()

    repo_root = Path(__file__).parent.parent

    # Load registry
    if args.from_registry:
        if args.registry_url:
            registry_url = args.registry_url
        else:
            # Try to get from local config or environment
            print("Error: --registry-url required when using --from-registry")
            return 1

        try:
            registry = load_remote_registry(registry_url)
        except Exception as e:
            print(f"Error: Failed to load remote registry: {e}")
            return 1
    else:
        registry = load_local_registry(repo_root)

    # Filter components
    components = filter_components(
        registry.get("components", {}),
        component_type=args.type,
        domain=args.domain,
        search=args.search,
    )

    # Print results
    print_components(components, show_details=args.details)

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
