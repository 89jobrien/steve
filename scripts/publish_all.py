#!/usr/bin/env python3
"""
Publish all components to GitHub Gists.

Publishes all markdown components in the steve/ directory to GitHub Gists.
Handles skills specially by linking reference files to their parent SKILL.md.

Usage:
    python scripts/publish_all.py [--public] [--update] [--dry-run]
    python scripts/publish_all.py steve/agents [--public]
    python scripts/publish_all.py steve/skills/code-review [--update]

Requires GITHUB_TOKEN environment variable.
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path


def find_markdown_files(base_path: Path, pattern: str = "**/*.md") -> list[Path]:
    """Find all markdown files matching pattern.

    Args:
        base_path: Directory to search in.
        pattern: Glob pattern for files.

    Returns:
        Sorted list of matching file paths.
    """
    if not base_path.exists():
        return []
    return sorted(base_path.glob(pattern))


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

    # Early return if not in skills directory
    if "skills" not in parts:
        return default_result

    # Find skills index safely
    skills_idx = list(parts).index("skills") if "skills" in parts else -1
    if skills_idx < 0 or skills_idx + 1 >= len(parts):
        return default_result

    skill_name = parts[skills_idx + 1]

    # Skip README.md at skills root level or invalid skill names
    if skill_name == "README.md":
        return default_result

    # Determine file type
    if file_path.name == "SKILL.md":
        return ("skill", skill_name)

    # Check subdirectory type
    subdir_map = {"references": "reference", "examples": "example", "scripts": "script"}
    file_type = "other"
    if skills_idx + 2 < len(parts):
        subdir = parts[skills_idx + 2]
        file_type = subdir_map.get(subdir, "other")

    return (file_type, skill_name)


def publish_file(
    file_path: Path,
    repo_root: Path,
    public: bool = False,
    update: bool = False,
) -> bool:
    """Publish a single file to GitHub Gist.

    Args:
        file_path: Path to the file.
        repo_root: Repository root path.
        public: Make gist public.
        update: Update existing gist if present.

    Returns:
        True if successful, False otherwise.
    """
    relative_path = file_path.relative_to(repo_root)
    cmd = ["uv", "run", "python", "scripts/publish_to_gist.py", str(relative_path)]

    if public:
        cmd.append("--public")
    if update:
        cmd.append("--update")

    try:
        result = subprocess.run(
            cmd,
            cwd=repo_root,
            check=True,
            capture_output=True,
            text=True,
        )
        # Extract gist URL from output
        for line in result.stdout.split("\n"):
            if "Gist published:" in line:
                print(f"  {line.strip()}")
                return True
        return True
    except subprocess.CalledProcessError as e:
        error_msg = e.stderr.strip() if e.stderr else "Unknown error"
        print(f"  [FAIL] {error_msg}")
        return False


def publish_skills_directory(
    base_path: Path,
    repo_root: Path,
    public: bool,
    update: bool,
    dry_run: bool,
    delay: float,
) -> tuple[int, int]:
    """Publish skills directory with special handling for references.

    Args:
        base_path: Path to skills directory.
        repo_root: Repository root path.
        public: Make gists public.
        update: Update existing gists.
        dry_run: Only show what would be done.
        delay: Delay between API calls in seconds.

    Returns:
        Tuple of (success_count, total_count).
    """
    files = find_markdown_files(base_path)

    if not files:
        print(f"No files found in {base_path}")
        return (0, 0)

    # Classify files
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

    # Calculate totals (excluding 'other' files)
    total_to_publish = len(skills) + len(references) + len(examples) + len(scripts)

    print(f"Found {len(files)} files:")
    print(f"  - {len(skills)} SKILL.md files")
    print(f"  - {len(references)} reference files")
    print(f"  - {len(examples)} example files")
    print(f"  - {len(scripts)} script files")
    print(f"  - {len(other)} other files (skipped)")
    print(f"\nWill publish {total_to_publish} files")
    print()

    if dry_run:
        if skills:
            print("SKILL.md files:")
            for f, _name in skills:
                print(f"  {f.relative_to(repo_root)}")
        if references:
            print("\nReference files:")
            for f, name in references:
                print(f"  {f.relative_to(repo_root)} (parent: {name})")
        if examples:
            print("\nExample files:")
            for f, name in examples:
                print(f"  {f.relative_to(repo_root)} (parent: {name})")
        if scripts:
            print("\nScript files:")
            for f, name in scripts:
                print(f"  {f.relative_to(repo_root)} (parent: {name})")
        return (0, 0)

    success_count = 0

    # Publish SKILL.md files first (parents before children)
    if skills:
        print("Publishing SKILL.md files...")
        for f, _skill_name in skills:
            print(f"  {f.relative_to(repo_root)}")
            if publish_file(f, repo_root, public, update):
                success_count += 1
            time.sleep(delay)

    # Publish reference files
    if references:
        print("\nPublishing reference files...")
        for f, skill_name in references:
            print(f"  {f.relative_to(repo_root)} (parent: {skill_name})")
            if publish_file(f, repo_root, public, update):
                success_count += 1
            time.sleep(delay)

    # Publish example files
    if examples:
        print("\nPublishing example files...")
        for f, skill_name in examples:
            print(f"  {f.relative_to(repo_root)} (parent: {skill_name})")
            if publish_file(f, repo_root, public, update):
                success_count += 1
            time.sleep(delay)

    # Publish script files
    if scripts:
        print("\nPublishing script files...")
        for f, skill_name in scripts:
            print(f"  {f.relative_to(repo_root)} (parent: {skill_name})")
            if publish_file(f, repo_root, public, update):
                success_count += 1
            time.sleep(delay)

    return (success_count, total_to_publish)


def publish_standard_directory(
    base_path: Path,
    repo_root: Path,
    public: bool,
    update: bool,
    dry_run: bool,
    delay: float,
) -> tuple[int, int]:
    """Publish a standard (non-skills) directory.

    Args:
        base_path: Path to directory.
        repo_root: Repository root path.
        public: Make gists public.
        update: Update existing gists.
        dry_run: Only show what would be done.
        delay: Delay between API calls in seconds.

    Returns:
        Tuple of (success_count, total_count).
    """
    files = find_markdown_files(base_path)

    # Filter out README.md files
    files = [f for f in files if f.name != "README.md"]

    if not files:
        print(f"No component files found in {base_path}")
        return (0, 0)

    print(f"Found {len(files)} component files\n")

    if dry_run:
        for f in files:
            print(f"  {f.relative_to(repo_root)}")
        return (0, 0)

    print("Publishing components...")
    success_count = 0

    for f in files:
        print(f"  {f.relative_to(repo_root)}")
        if publish_file(f, repo_root, public, update):
            success_count += 1
        time.sleep(delay)

    return (success_count, len(files))


def main() -> int:
    """Publish all components to GitHub Gists."""
    parser = argparse.ArgumentParser(description="Publish all components to GitHub Gists")
    parser.add_argument(
        "path",
        nargs="?",
        default="steve",
        help="Path to publish (default: steve/)",
    )
    parser.add_argument("--public", action="store_true", help="Make gists public")
    parser.add_argument("--update", action="store_true", help="Update existing gists")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be published")
    parser.add_argument(
        "--delay",
        type=float,
        default=0.5,
        help="Delay between API calls in seconds (default: 0.5)",
    )

    args = parser.parse_args()

    repo_root = Path(__file__).parent.parent
    base_path = repo_root / args.path

    if not base_path.exists():
        print(f"Error: Path not found: {base_path}")
        return 1

    # Check if this is a skills directory
    is_skills = "skills" in base_path.parts or base_path.name == "skills"

    # If publishing all of steve/, process each component type
    if base_path.name == "steve" and base_path.is_dir():
        total_success = 0
        total_count = 0

        component_dirs = ["agents", "commands", "hooks", "skills", "templates"]

        for component_type in component_dirs:
            component_path = base_path / component_type
            if not component_path.exists():
                continue

            print(f"\n{'=' * 60}")
            print(f"Publishing {component_type}/")
            print("=" * 60)

            if component_type == "skills":
                success, count = publish_skills_directory(
                    component_path, repo_root, args.public, args.update, args.dry_run, args.delay
                )
            else:
                success, count = publish_standard_directory(
                    component_path, repo_root, args.public, args.update, args.dry_run, args.delay
                )

            total_success += success
            total_count += count

        if not args.dry_run and total_count > 0:
            print(f"\n{'=' * 60}")
            print(f"TOTAL: Published {total_success}/{total_count} components successfully")
            print("=" * 60)

        return 0 if total_success == total_count else 1

    # Single directory
    if is_skills:
        success_count, total_count = publish_skills_directory(
            base_path, repo_root, args.public, args.update, args.dry_run, args.delay
        )
    else:
        success_count, total_count = publish_standard_directory(
            base_path, repo_root, args.public, args.update, args.dry_run, args.delay
        )

    if args.dry_run:
        return 0

    if total_count == 0:
        return 1

    print(f"\nPublished {success_count}/{total_count} components successfully")
    return 0 if success_count == total_count else 1


if __name__ == "__main__":
    sys.exit(main())
