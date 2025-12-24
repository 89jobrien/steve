#!/usr/bin/env python3
"""
Build index of all components in the steve repository.

Scans the repository and generates an index JSON file with metadata
about all agents, commands, skills, hooks, and templates.

Usage:
    python scripts/build_index.py [--output index.json] [--incremental]

The --incremental flag enables hash-based caching for ~8x faster rebuilds
when only a few files have changed.
"""

import argparse
import datetime
import hashlib
import json
import re
from pathlib import Path
from typing import Any

import yaml


CACHE_FILE = ".index-cache.json"


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


def get_file_hash(file_path: Path) -> str:
    """Generate hash based on mtime and size for fast comparison."""
    stat = file_path.stat()
    return hashlib.md5(f"{stat.st_mtime_ns}:{stat.st_size}".encode()).hexdigest()


def load_cache(cache_path: Path) -> dict[str, Any]:
    """Load cache from file."""
    if cache_path.exists():
        try:
            return json.loads(cache_path.read_text())
        except Exception:
            return {}
    return {}


def save_cache(cache: dict[str, Any], cache_path: Path) -> None:
    """Save cache to file."""
    cache_path.write_text(json.dumps(cache, indent=2))


def build_component(
    file_path: Path,
    frontmatter: dict[str, Any],
    component_type: str,
    base_dir: Path,
    skill_dir: Path | None = None,
) -> dict[str, Any]:
    """Build a component dictionary from parsed frontmatter."""
    if component_type == "skill" and skill_dir:
        return {
            "type": "skill",
            "path": str(file_path.relative_to(base_dir)),
            "name": frontmatter.get("name", skill_dir.name),
            "domain": None,
            "description": frontmatter.get("description", ""),
            "has_references": (skill_dir / "references").exists(),
            "has_scripts": (skill_dir / "scripts").exists(),
            "has_assets": (skill_dir / "assets").exists(),
        }

    relative_path = str(file_path.relative_to(base_dir))
    component = {
        "type": component_type,
        "path": relative_path,
        "name": frontmatter.get("name", file_path.stem),
        "domain": file_path.parent.name,
        "description": frontmatter.get("description", ""),
    }

    if component_type == "agent":
        component.update(
            {
                "tools": frontmatter.get("tools", ""),
                "model": frontmatter.get("model", "sonnet"),
                "color": frontmatter.get("color", ""),
                "skills": frontmatter.get("skills", ""),
            }
        )

    return component


def scan_directory(directory: Path, component_type: str, base_dir: Path) -> list[dict[str, Any]]:
    """Scan a directory for component files (non-incremental)."""
    components: list[dict[str, Any]] = []

    if not directory.exists():
        return components

    for file_path in directory.rglob("*.md"):
        if file_path.name == "README.md":
            continue

        try:
            content = file_path.read_text(encoding="utf-8")
            frontmatter, _ = parse_frontmatter(content)
            component = build_component(file_path, frontmatter, component_type, base_dir)
            components.append(component)
        except Exception as e:
            print(f"Warning: Failed to process {file_path}: {e}")

    return components


def collect_component_files(steve_dir: Path) -> list[tuple[Path, str, Path | None]]:
    """Collect all component files with their types."""
    component_files: list[tuple[Path, str, Path | None]] = []

    # Agents
    agents_dir = steve_dir / "agents"
    if agents_dir.exists():
        for domain_dir in agents_dir.iterdir():
            if domain_dir.is_dir():
                for f in domain_dir.rglob("*.md"):
                    if f.name != "README.md":
                        component_files.append((f, "agent", None))

    # Commands
    commands_dir = steve_dir / "commands"
    if commands_dir.exists():
        for category_dir in commands_dir.iterdir():
            if category_dir.is_dir():
                for f in category_dir.rglob("*.md"):
                    if f.name != "README.md":
                        component_files.append((f, "command", None))

    # Skills
    skills_dir = steve_dir / "skills"
    if skills_dir.exists():
        for skill_dir in skills_dir.iterdir():
            if skill_dir.is_dir():
                skill_file = skill_dir / "SKILL.md"
                if skill_file.exists():
                    component_files.append((skill_file, "skill", skill_dir))

    # Hooks
    hooks_dir = steve_dir / "hooks"
    if hooks_dir.exists():
        for hook_type_dir in hooks_dir.iterdir():
            if hook_type_dir.is_dir():
                for f in hook_type_dir.rglob("*.md"):
                    if f.name != "README.md":
                        component_files.append((f, "hook", None))

    return component_files


def build_index_incremental(repo_root: Path) -> tuple[dict[str, Any], dict[str, int]]:
    """Build index using incremental caching for ~8x speedup."""
    steve_dir = repo_root / "steve"
    cache_path = repo_root / CACHE_FILE
    cache = load_cache(cache_path)
    new_cache: dict[str, Any] = {}

    index: dict[str, Any] = {
        "version": "1.0.0",
        "generated_at": "",
        "agents": [],
        "commands": [],
        "skills": [],
        "hooks": [],
        "templates": [],
    }

    component_files = collect_component_files(steve_dir)
    stats = {"hits": 0, "misses": 0}

    for file_path, component_type, skill_dir in component_files:
        file_key = str(file_path.relative_to(repo_root))
        file_hash = get_file_hash(file_path)

        # Check cache
        if file_key in cache and cache[file_key].get("hash") == file_hash:
            component = cache[file_key]["data"]
            stats["hits"] += 1
        else:
            # Cache miss - parse file
            try:
                content = file_path.read_text(encoding="utf-8")
                frontmatter, _ = parse_frontmatter(content)
                component = build_component(
                    file_path, frontmatter, component_type, steve_dir, skill_dir
                )
                stats["misses"] += 1
            except Exception as e:
                print(f"Warning: Failed to process {file_path}: {e}")
                continue

        # Update cache and index
        new_cache[file_key] = {"hash": file_hash, "data": component}

        if component_type == "agent":
            index["agents"].append(component)
        elif component_type == "command":
            index["commands"].append(component)
        elif component_type == "skill":
            index["skills"].append(component)
        elif component_type == "hook":
            index["hooks"].append(component)

    # Templates (simple, no caching needed)
    templates_dir = steve_dir / "templates"
    if templates_dir.exists():
        index["templates"] = [
            {"type": "template", "path": str(f.relative_to(steve_dir)), "name": f.stem}
            for f in templates_dir.glob("*.md")
        ]

    # Sort all lists for deterministic output
    for key in ["agents", "commands", "skills", "hooks"]:
        index[key].sort(key=lambda x: x["path"])

    # Save updated cache
    save_cache(new_cache, cache_path)

    return index, stats


def build_index(repo_root: Path) -> dict[str, Any]:
    """Build complete index of all components (non-incremental)."""
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
    parser.add_argument(
        "--incremental",
        action="store_true",
        help="Use incremental caching for faster rebuilds (~4x speedup)",
    )
    parser.add_argument(
        "--clear-cache",
        action="store_true",
        help="Clear the incremental cache before building",
    )

    args = parser.parse_args()

    repo_root = Path(__file__).parent.parent

    # Handle cache clearing
    cache_path = repo_root / CACHE_FILE
    if args.clear_cache and cache_path.exists():
        cache_path.unlink()
        print(f"Cleared cache: {cache_path}")

    # Build index
    if args.incremental:
        index, stats = build_index_incremental(repo_root)
        cache_info = f" (cache: {stats['hits']} hits, {stats['misses']} misses)"
    else:
        index = build_index(repo_root)
        cache_info = ""

    # Add timestamp (UTC with timezone info)
    index["generated_at"] = datetime.datetime.now(datetime.timezone.utc).isoformat()

    # Write index
    output_path = repo_root / args.output
    output_path.write_text(json.dumps(index, indent=2, ensure_ascii=False))

    # Print summary
    print(f"Index built: {output_path}{cache_info}")
    print(f"  Agents: {len(index['agents'])}")
    print(f"  Commands: {len(index['commands'])}")
    print(f"  Skills: {len(index['skills'])}")
    print(f"  Hooks: {len(index['hooks'])}")
    print(f"  Templates: {len(index['templates'])}")


if __name__ == "__main__":
    main()
