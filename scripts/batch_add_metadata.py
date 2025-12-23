#!/usr/bin/env python3
"""
Batch add metadata to component files.

Adds metadata to multiple component frontmatter files at once.
Handles skills specially by linking reference files to their parent SKILL.md.

Usage:
    python scripts/batch_add_metadata.py steve/agents --key version 1.0
    python scripts/batch_add_metadata.py steve/skills --key author joe
    python scripts/batch_add_metadata.py steve/commands --dry-run
"""

import argparse
import subprocess
import sys
from pathlib import Path


def find_markdown_files(base_path: str, pattern: str = "**/*.md") -> list[Path]:
    """Find all markdown files matching pattern.

    Args:
        base_path: Directory to search in.
        pattern: Glob pattern for files.

    Returns:
        Sorted list of matching file paths.
    """
    base = Path(base_path)
    if not base.exists():
        return []
    return sorted(base.glob(pattern))


def classify_skill_file(file_path: Path) -> tuple[str, str | None]:
    """Classify a file within a skill directory.

    Args:
        file_path: Path to the file.

    Returns:
        Tuple of (file_type, parent_skill_name or None).
        file_type is one of: 'skill', 'reference', 'example', 'script', 'other'
    """
    parts = file_path.parts
    default_result: tuple[str, str | None] = ("other", None)

    # Check if this is in a skills directory
    if "skills" not in parts:
        return default_result

    # Find the skill directory (the directory after 'skills')
    try:
        skills_idx = parts.index("skills")
    except ValueError:
        return default_result

    # Validate we have enough path components
    if skills_idx + 1 >= len(parts):
        return default_result

    skill_name = parts[skills_idx + 1]

    # Skip README.md at skills root level
    if skill_name == "README.md":
        return default_result

    # Check if it's the main SKILL.md file
    if file_path.name == "SKILL.md":
        return ("skill", skill_name)

    # Check subdirectory type
    subdir_map = {"references": "reference", "examples": "example", "scripts": "script"}
    file_type = "other"
    if skills_idx + 2 < len(parts):
        subdir = parts[skills_idx + 2]
        file_type = subdir_map.get(subdir, "other")

    return (file_type, skill_name)


def add_metadata(file_path: Path, metadata: dict[str, str]) -> bool:
    """Add metadata to a file using add_metadata.py.

    Args:
        file_path: Path to the component file.
        metadata: Key-value pairs to add.

    Returns:
        True if successful, False otherwise.
    """
    cmd = ["uv", "run", "python", "scripts/add_metadata.py", str(file_path)]

    for key, value in metadata.items():
        cmd.extend(["--key", key, str(value)])

    try:
        subprocess.run(cmd, check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip() if e.stderr else "Unknown error"
        print(f"  [FAIL] {file_path}: {error_msg}")
        return False


def process_skills_directory(
    base_path: str,
    pattern: str,
    metadata: dict[str, str],
    dry_run: bool,
) -> tuple[int, int]:
    """Process skills directory with special handling for references.

    Args:
        base_path: Path to skills directory.
        pattern: Glob pattern for files.
        metadata: Base metadata to add.
        dry_run: If True, only show what would be done.

    Returns:
        Tuple of (success_count, total_count).
    """
    files = find_markdown_files(base_path, pattern)

    if not files:
        print(f"No files found in {base_path} matching {pattern}")
        return (0, 0)

    # Classify all files
    skills: list[tuple[Path, str]] = []
    references: list[tuple[Path, str]] = []
    examples: list[tuple[Path, str]] = []
    scripts: list[tuple[Path, str]] = []
    other: list[Path] = []

    for f in files:
        file_type, skill_name = classify_skill_file(f)
        if file_type == "skill" and skill_name:
            skills.append((f, skill_name))
        elif file_type == "reference" and skill_name:
            references.append((f, skill_name))
        elif file_type == "example" and skill_name:
            examples.append((f, skill_name))
        elif file_type == "script" and skill_name:
            scripts.append((f, skill_name))
        else:
            other.append(f)

    print(f"Found {len(files)} files:")
    print(f"  - {len(skills)} SKILL.md files")
    print(f"  - {len(references)} reference files")
    print(f"  - {len(examples)} example files")
    print(f"  - {len(scripts)} script files")
    print(f"  - {len(other)} other files")
    print()

    if dry_run:
        if skills:
            print("SKILL.md files (type: skill):")
            for f, _name in skills:
                print(f"  {f}")
        if references:
            print("\nReference files (type: reference, linked to parent):")
            for f, name in references:
                print(f"  {f} -> parent: {name}")
        if examples:
            print("\nExample files (type: example, linked to parent):")
            for f, name in examples:
                print(f"  {f} -> parent: {name}")
        if scripts:
            print("\nScript files (type: script, linked to parent):")
            for f, name in scripts:
                print(f"  {f} -> parent: {name}")
        if other:
            print("\nOther files (skipped):")
            for f in other:
                print(f"  {f}")
        return (0, 0)

    success_count = 0
    total_count = 0

    # Process SKILL.md files
    if skills:
        print("Processing SKILL.md files...")
        for f, _skill_name in skills:
            total_count += 1
            skill_metadata = {**metadata, "type": "skill"}
            if add_metadata(f, skill_metadata):
                print(f"  [OK] {f}")
                success_count += 1

    # Process reference files
    if references:
        print("\nProcessing reference files...")
        for f, skill_name in references:
            total_count += 1
            ref_metadata = {
                **metadata,
                "type": "reference",
                "parent": skill_name,
            }
            if add_metadata(f, ref_metadata):
                print(f"  [OK] {f}")
                success_count += 1

    # Process example files
    if examples:
        print("\nProcessing example files...")
        for f, skill_name in examples:
            total_count += 1
            ex_metadata = {
                **metadata,
                "type": "example",
                "parent": skill_name,
            }
            if add_metadata(f, ex_metadata):
                print(f"  [OK] {f}")
                success_count += 1

    # Process script files
    if scripts:
        print("\nProcessing script files...")
        for f, skill_name in scripts:
            total_count += 1
            script_metadata = {
                **metadata,
                "type": "script",
                "parent": skill_name,
            }
            if add_metadata(f, script_metadata):
                print(f"  [OK] {f}")
                success_count += 1

    return (success_count, total_count)


def process_standard_directory(
    base_path: str,
    pattern: str,
    metadata: dict[str, str],
    dry_run: bool,
) -> tuple[int, int]:
    """Process a standard (non-skills) directory.

    Args:
        base_path: Path to directory.
        pattern: Glob pattern for files.
        metadata: Metadata to add.
        dry_run: If True, only show what would be done.

    Returns:
        Tuple of (success_count, total_count).
    """
    files = find_markdown_files(base_path, pattern)

    if not files:
        print(f"No files found in {base_path} matching {pattern}")
        return (0, 0)

    print(f"Found {len(files)} files\n")

    if dry_run:
        for f in files:
            print(f"  {f}")
        return (0, 0)

    # Process files
    print(f"Adding metadata: {metadata}\n")
    success_count = 0

    for file in files:
        if add_metadata(file, metadata):
            print(f"  [OK] {file}")
            success_count += 1

    return (success_count, len(files))


def main() -> int:
    """Batch add metadata to component files."""
    parser = argparse.ArgumentParser(description="Batch add metadata to components")
    parser.add_argument("base_path", help="Base path to search (e.g., steve/agents)")
    parser.add_argument("--pattern", default="**/*.md", help="Glob pattern for files")
    parser.add_argument(
        "--key",
        action="append",
        nargs=2,
        metavar=("KEY", "VALUE"),
        help="Metadata key-value pair (can be repeated)",
    )
    parser.add_argument("--dry-run", action="store_true", help="Show files without processing")

    args = parser.parse_args()

    # Build metadata dict
    metadata: dict[str, str] = dict(args.key) if args.key else {}

    if not metadata and not args.dry_run:
        print("Error: No metadata specified. Use --key KEY VALUE")
        return 1

    # Check if this is a skills directory - use special handling
    base = Path(args.base_path)
    is_skills = "skills" in base.parts or base.name == "skills"

    if is_skills:
        success_count, total_count = process_skills_directory(
            args.base_path, args.pattern, metadata, args.dry_run
        )
    else:
        success_count, total_count = process_standard_directory(
            args.base_path, args.pattern, metadata, args.dry_run
        )

    if args.dry_run:
        return 0

    if total_count == 0:
        return 1

    print(f"\nProcessed {success_count}/{total_count} files successfully")
    return 0 if success_count == total_count else 1


if __name__ == "__main__":
    sys.exit(main())
