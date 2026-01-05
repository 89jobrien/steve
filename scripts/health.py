#!/usr/bin/env python3
"""
Workspace health report for the steve repository.

Generates a comprehensive health report including component counts,
storage breakdown by directory, and warnings for issues.

Usage:
    python scripts/health.py [--json]

    --json: Output in JSON format
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from rich.console import Console
from rich.table import Table

from scripts.utils import (
    count_dirs,
    count_files,
    format_size,
    get_dir_size,
    get_repo_root,
    get_steve_dir,
)


console = Console()


def get_component_counts(steve_dir: Path) -> dict[str, int]:
    """Get counts of each component type."""
    counts = {
        "agents": 0,
        "commands": 0,
        "skills": 0,
        "hooks": 0,
        "templates": 0,
    }

    # Count agents (in subdirectories)
    agents_dir = steve_dir / "agents"
    if agents_dir.exists():
        for domain_dir in agents_dir.iterdir():
            if domain_dir.is_dir():
                counts["agents"] += count_files(domain_dir, ".md")
                # Subtract README.md files
                if (domain_dir / "README.md").exists():
                    counts["agents"] -= 1

    # Count commands (in subdirectories)
    commands_dir = steve_dir / "commands"
    if commands_dir.exists():
        for category_dir in commands_dir.iterdir():
            if category_dir.is_dir():
                counts["commands"] += count_files(category_dir, ".md")
                if (category_dir / "README.md").exists():
                    counts["commands"] -= 1

    # Count skills (each skill is a directory)
    skills_dir = steve_dir / "skills"
    if skills_dir.exists():
        counts["skills"] = count_dirs(skills_dir)

    # Count hooks (in subdirectories)
    hooks_dir = steve_dir / "hooks"
    if hooks_dir.exists():
        for hook_type_dir in hooks_dir.iterdir():
            if hook_type_dir.is_dir():
                counts["hooks"] += count_files(hook_type_dir, ".md")
                if (hook_type_dir / "README.md").exists():
                    counts["hooks"] -= 1

    # Count templates
    templates_dir = steve_dir / "templates"
    if templates_dir.exists():
        counts["templates"] = count_files(templates_dir, ".md")

    return counts


def get_storage_breakdown(steve_dir: Path) -> list[tuple[str, int]]:
    """Get storage breakdown by directory."""
    directories = [
        ("agents", steve_dir / "agents"),
        ("commands", steve_dir / "commands"),
        ("skills", steve_dir / "skills"),
        ("hooks", steve_dir / "hooks"),
        ("templates", steve_dir / "templates"),
        ("helpers", steve_dir / "helpers"),
        ("rules", steve_dir / "rules"),
    ]

    breakdown = []
    for name, path in directories:
        if path.exists():
            size = get_dir_size(path)
            breakdown.append((name, size))

    return breakdown


def get_warnings(steve_dir: Path, counts: dict[str, int]) -> list[str]:
    """Generate warnings based on health checks."""
    warnings = []

    # Check for large directories
    for name, path in [
        ("agents", steve_dir / "agents"),
        ("skills", steve_dir / "skills"),
    ]:
        if path.exists():
            size_mb = get_dir_size(path) / (1024 * 1024)
            if size_mb > 50:
                warnings.append(f"{name} directory is large ({size_mb:.1f} MB)")

    # Check for missing required directories
    required_dirs = ["agents", "commands", "skills"]
    for dir_name in required_dirs:
        if not (steve_dir / dir_name).exists():
            warnings.append(f"Missing {dir_name} directory")

    # Check for low component counts
    if counts["agents"] < 5:
        warnings.append(f"Low agent count ({counts['agents']})")
    if counts["skills"] < 3:
        warnings.append(f"Low skill count ({counts['skills']})")

    return warnings


def run_health(json_output: bool = False) -> int:
    """Run the health check and display results."""
    repo_root = get_repo_root()
    steve_dir = get_steve_dir(repo_root)

    if not steve_dir.exists():
        console.print("[red]Error: steve directory not found[/red]")
        return 1

    counts = get_component_counts(steve_dir)
    storage = get_storage_breakdown(steve_dir)
    warnings = get_warnings(steve_dir, counts)
    total_size = sum(size for _, size in storage)

    if json_output:
        result = {
            "workspace": {
                "name": "steve",
                "path": str(steve_dir),
                "generated_at": datetime.now(timezone.utc).isoformat(),
            },
            "components": counts,
            "storage": {
                "breakdown": dict(storage),
                "total_bytes": total_size,
                "total_formatted": format_size(total_size),
            },
            "warnings": warnings,
            "health_score": max(0, 100 - len(warnings) * 10),
        }
        print(json.dumps(result, indent=2))
        return 0

    # Rich output
    console.print()
    console.print("[bold cyan]Steve Workspace Health[/bold cyan]")
    console.print(f"[dim]{steve_dir}[/dim]")
    console.print()

    # Components table
    comp_table = Table(title="Components", show_header=True, header_style="bold")
    comp_table.add_column("Type", style="cyan")
    comp_table.add_column("Count", justify="right")

    for comp_type, count in counts.items():
        comp_table.add_row(comp_type.capitalize(), str(count))

    comp_table.add_row("[bold]Total[/bold]", f"[bold]{sum(counts.values())}[/bold]")
    console.print(comp_table)
    console.print()

    # Storage table
    storage_table = Table(title="Storage", show_header=True, header_style="bold")
    storage_table.add_column("Directory", style="cyan")
    storage_table.add_column("Size", justify="right")

    for name, size in storage:
        storage_table.add_row(name, format_size(size))

    storage_table.add_row("[bold]Total[/bold]", f"[bold]{format_size(total_size)}[/bold]")
    console.print(storage_table)
    console.print()

    # Warnings
    if warnings:
        console.print("[bold yellow]Warnings:[/bold yellow]")
        for warning in warnings:
            console.print(f"  [yellow]![/yellow] {warning}")
    else:
        console.print("[green]No warnings[/green]")

    console.print()
    health_score = max(0, 100 - len(warnings) * 10)
    console.print(f"Health Score: [bold]{health_score}%[/bold]")

    return 0


def main() -> None:
    """Entry point for the health command."""
    parser = argparse.ArgumentParser(description="Generate workspace health report for steve")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format",
    )

    args = parser.parse_args()
    sys.exit(run_health(json_output=args.json))


if __name__ == "__main__":
    main()
