#!/usr/bin/env python3
"""
Install a component by name from the gist registry.

Searches the registry for a component by name and installs it.

Usage:
    python scripts/install_component.py <component-name> [--type TYPE] [--domain DOMAIN]
    python scripts/install_component.py <component-name> --from-registry [--registry-url URL]
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

import requests


def load_local_registry(repo_root: Path) -> dict[str, Any]:
    """Load local gist registry."""
    registry_path = repo_root / ".gist-registry.json"
    if registry_path.exists():
        return json.loads(registry_path.read_text())
    return {"components": {}}


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


def find_component(
    components: dict[str, Any],
    name: str,
    component_type: str | None = None,
    domain: str | None = None,
) -> dict[str, Any] | None:
    """Find a component by name, optionally filtered by type and domain."""
    matches = []

    for component in components.values():
        component_name = component.get("name", "").lower()
        if component_name == name.lower():
            # Check filters
            if component_type and component.get("type") != component_type:
                continue
            if domain and component.get("domain") != domain:
                continue
            matches.append(component)

    if len(matches) == 1:
        return matches[0]
    if len(matches) > 1:
        print(f"Multiple components found with name '{name}':")
        for i, comp in enumerate(matches, 1):
            print(
                f"  {i}. {comp.get('name')} ({comp.get('type')}) - {comp.get('domain', 'no domain')}"
            )
        print("\nUse --type and/or --domain to narrow down the search.")
        return None
    return None


def main() -> int:
    parser = argparse.ArgumentParser(description="Install component by name from registry")
    parser.add_argument("component_name", help="Name of component to install")
    parser.add_argument(
        "--type", choices=["agent", "command", "skill", "hook"], help="Filter by component type"
    )
    parser.add_argument("--domain", help="Filter by domain/category")
    parser.add_argument(
        "--from-registry", action="store_true", help="Load from remote registry Gist"
    )
    parser.add_argument("--registry-url", help="URL of registry Gist (default: from local config)")

    args = parser.parse_args()

    repo_root = Path(__file__).parent.parent

    # Load registry
    if args.from_registry:
        if args.registry_url:
            registry_url = args.registry_url
        else:
            print("Error: --registry-url required when using --from-registry")
            return 1

        try:
            registry = load_remote_registry(registry_url)
        except Exception as e:
            print(f"Error: Failed to load remote registry: {e}")
            return 1
    else:
        registry = load_local_registry(repo_root)

    # Find component
    component = find_component(
        registry.get("components", {}),
        args.component_name,
        component_type=args.type,
        domain=args.domain,
    )

    if not component:
        print(f"Error: Component '{args.component_name}' not found in registry.")
        print("\nAvailable components:")
        for comp in registry.get("components", {}).values():
            print(f"  - {comp.get('name')} ({comp.get('type')})")
        return 1

    # Get gist URL
    gist_url = component.get("gist_url")
    if not gist_url:
        print(f"Error: Component '{args.component_name}' has no gist_url")
        return 1

    # Install using install_from_gist.py
    print(f"Installing {component.get('name')} from {gist_url}...")

    result = subprocess.run(
        [sys.executable, "scripts/install_from_gist.py", gist_url], check=False, cwd=repo_root
    )

    if result.returncode == 0:
        print(f"✓ Successfully installed {component.get('name')}")
        return 0
    print("Error: Failed to install component")
    return 1


if __name__ == "__main__":
    import sys

    sys.exit(main())
