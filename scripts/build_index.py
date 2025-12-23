#!/usr/bin/env python3
"""
Build index of all components in the steve repository.

Scans the repository and generates an index JSON file with metadata
about all agents, commands, skills, hooks, and templates.

Usage:
    python scripts/build_index.py [--output index.json]
"""

import argparse
import datetime
import json
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


def scan_directory(directory: Path, component_type: str, base_dir: Path) -> list[dict[str, Any]]:
    """Scan a directory for component files."""
    components: list[dict[str, Any]] = []

    if not directory.exists():
        return components

    for file_path in directory.rglob("*.md"):
        if file_path.name == "README.md":
            continue

        try:
            content = file_path.read_text(encoding="utf-8")
            frontmatter, _ = parse_frontmatter(content)

            # Extract basic info
            relative_path = str(file_path.relative_to(base_dir))
            domain = file_path.parent.name if file_path.parent != directory else None

            component = {
                "type": component_type,
                "path": relative_path,
                "name": frontmatter.get("name", file_path.stem),
                "domain": domain,
                "description": frontmatter.get("description", ""),
            }

            # Add type-specific fields
            if component_type == "agent":
                component.update(
                    {
                        "tools": frontmatter.get("tools", ""),
                        "model": frontmatter.get("model", "sonnet"),
                        "color": frontmatter.get("color", ""),
                        "skills": frontmatter.get("skills", ""),
                    }
                )
            elif component_type == "skill":
                component.update(
                    {
                        "has_references": (file_path.parent / "references").exists(),
                        "has_scripts": (file_path.parent / "scripts").exists(),
                        "has_assets": (file_path.parent / "assets").exists(),
                    }
                )

            components.append(component)
        except Exception as e:
            print(f"Warning: Failed to process {file_path}: {e}")

    return components


def build_index(repo_root: Path) -> dict[str, Any]:
    """Build complete index of all components."""
    steve_dir = repo_root / "steve"

    index: dict[str, Any] = {
        "version": "1.0.0",
        "generated_at": "",
        "agents": [],
        "commands": [],
        "skills": [],
        "hooks": [],
        "templates": [],
    }

    # Scan agents
    agents_dir = steve_dir / "agents"
    for domain_dir in agents_dir.iterdir():
        if domain_dir.is_dir():
            index["agents"].extend(scan_directory(domain_dir, "agent", steve_dir))

    # Scan commands
    commands_dir = steve_dir / "commands"
    for category_dir in commands_dir.iterdir():
        if category_dir.is_dir():
            index["commands"].extend(scan_directory(category_dir, "command", steve_dir))

    # Scan skills
    skills_dir = steve_dir / "skills"
    for skill_dir in skills_dir.iterdir():
        if skill_dir.is_dir():
            skill_file = skill_dir / "SKILL.md"
            if skill_file.exists():
                try:
                    content = skill_file.read_text(encoding="utf-8")
                    frontmatter, _ = parse_frontmatter(content)

                    component = {
                        "type": "skill",
                        "path": str(skill_file.relative_to(steve_dir)),
                        "name": frontmatter.get("name", skill_dir.name),
                        "domain": None,
                        "description": frontmatter.get("description", ""),
                        "has_references": (skill_dir / "references").exists(),
                        "has_scripts": (skill_dir / "scripts").exists(),
                        "has_assets": (skill_dir / "assets").exists(),
                    }
                    index["skills"].append(component)
                except Exception as e:
                    print(f"Warning: Failed to process {skill_file}: {e}")

    # Scan hooks
    hooks_dir = steve_dir / "hooks"
    for hook_type_dir in hooks_dir.iterdir():
        if hook_type_dir.is_dir():
            index["hooks"].extend(scan_directory(hook_type_dir, "hook", steve_dir))

    # Scan templates
    templates_dir = steve_dir / "templates"
    if templates_dir.exists():
        index["templates"] = [
            {
                "type": "template",
                "path": str(f.relative_to(steve_dir)),
                "name": f.stem,
            }
            for f in templates_dir.glob("*.md")
        ]

    return index


def main() -> None:
    """Build and write the component index."""
    parser = argparse.ArgumentParser(description="Build index of steve repository components")
    parser.add_argument(
        "--output", default="index.json", help="Output file path (default: index.json)"
    )

    args = parser.parse_args()

    repo_root = Path(__file__).parent.parent
    index = build_index(repo_root)

    # Add timestamp (UTC with timezone info)
    index["generated_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()

    # Write index
    output_path = repo_root / args.output
    output_path.write_text(json.dumps(index, indent=2, ensure_ascii=False))

    # Print summary
    print(f"Index built: {output_path}")
    print(f"  Agents: {len(index['agents'])}")
    print(f"  Commands: {len(index['commands'])}")
    print(f"  Skills: {len(index['skills'])}")
    print(f"  Hooks: {len(index['hooks'])}")
    print(f"  Templates: {len(index['templates'])}")


if __name__ == "__main__":
    main()
