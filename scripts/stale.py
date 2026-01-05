#!/usr/bin/env python3
"""
Stale component detection for the steve repository.

Finds components that haven't been modified recently, helping identify
potentially outdated or unmaintained components.

Usage:
    python scripts/stale.py [--days N] [--json]

    --days N: Consider files stale after N days (default: 90)
    --json: Output in JSON format
"""

import argparse
import json
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from rich.console import Console
from rich.table import Table

from scripts.utils import (
    collect_agents,
    collect_commands,
    collect_hooks,
    collect_skills,
    get_repo_root,
    get_steve_dir,
)


console = Console()


@dataclass
class StaleComponent:
    """Represents a stale component."""

    path: str
    component_type: str
    days_old: int
    last_modified: datetime


def get_file_age(file_path: Path) -> tuple[int, datetime]:
    """Get file age in days and last modified time."""
    mtime = file_path.stat().st_mtime
    modified = datetime.fromtimestamp(mtime, tz=timezone.utc)
    now = datetime.now(timezone.utc)
    age_days = (now - modified).days
    return age_days, modified


def find_stale_components(steve_dir: Path, threshold_days: int) -> list[StaleComponent]:
    """Find all components older than threshold days."""
    stale = []

    # Check agents
    for agent_file in collect_agents(steve_dir):
        try:
            age_days, modified = get_file_age(agent_file)
            if age_days >= threshold_days:
                rel_path = str(agent_file.relative_to(steve_dir))
                stale.append(StaleComponent(rel_path, "agent", age_days, modified))
        except (OSError, PermissionError):
            continue

    # Check commands
    for command_file in collect_commands(steve_dir):
        try:
            age_days, modified = get_file_age(command_file)
            if age_days >= threshold_days:
                rel_path = str(command_file.relative_to(steve_dir))
                stale.append(StaleComponent(rel_path, "command", age_days, modified))
        except (OSError, PermissionError):
            continue

    # Check skills (use SKILL.md modification time)
    for skill_dir, skill_file in collect_skills(steve_dir):
        try:
            age_days, modified = get_file_age(skill_file)
            if age_days >= threshold_days:
                rel_path = str(skill_dir.relative_to(steve_dir))
                stale.append(StaleComponent(rel_path, "skill", age_days, modified))
        except (OSError, PermissionError):
            continue

    # Check hooks
    for hook_file in collect_hooks(steve_dir):
        try:
            age_days, modified = get_file_age(hook_file)
            if age_days >= threshold_days:
                rel_path = str(hook_file.relative_to(steve_dir))
                stale.append(StaleComponent(rel_path, "hook", age_days, modified))
        except (OSError, PermissionError):
            continue

    # Sort by age (oldest first)
    stale.sort(key=lambda x: x.days_old, reverse=True)

    return stale


def run_stale(threshold_days: int = 90, json_output: bool = False) -> int:
    """Run the stale component check and display results."""
    repo_root = get_repo_root()
    steve_dir = get_steve_dir(repo_root)

    if not steve_dir.exists():
        console.print("[red]Error: steve directory not found[/red]")
        return 1

    stale_components = find_stale_components(steve_dir, threshold_days)

    if json_output:
        output = {
            "workspace": "steve",
            "threshold_days": threshold_days,
            "stale_count": len(stale_components),
            "components": [
                {
                    "path": c.path,
                    "type": c.component_type,
                    "days_old": c.days_old,
                    "last_modified": c.last_modified.isoformat(),
                }
                for c in stale_components
            ],
        }
        print(json.dumps(output, indent=2))
        return 0

    # Rich output
    console.print()
    console.print("[bold cyan]Stale Component Detection[/bold cyan]")
    console.print(f"[dim]Threshold: {threshold_days} days[/dim]")
    console.print()

    if not stale_components:
        console.print(f"[green]No components older than {threshold_days} days[/green]")
        return 0

    # Group by type
    by_type: dict[str, list[StaleComponent]] = {}
    for component in stale_components:
        by_type.setdefault(component.component_type, []).append(component)

    # Display by type
    for comp_type in ["agent", "command", "skill", "hook"]:
        components = by_type.get(comp_type, [])
        if not components:
            continue

        table = Table(
            title=f"Stale {comp_type.capitalize()}s ({len(components)})",
            show_header=True,
            header_style="bold",
        )
        table.add_column("Path", style="cyan")
        table.add_column("Age", justify="right")
        table.add_column("Last Modified")

        for comp in components:
            age_str = f"{comp.days_old} days"
            date_str = comp.last_modified.strftime("%Y-%m-%d")
            table.add_row(comp.path, age_str, date_str)

        console.print(table)
        console.print()

    # Summary
    console.print(
        f"Found [bold]{len(stale_components)}[/bold] stale components "
        f"(older than {threshold_days} days)"
    )

    return 0


def main() -> None:
    """Entry point for the stale command."""
    parser = argparse.ArgumentParser(description="Find stale components in steve repository")
    parser.add_argument(
        "--days",
        type=int,
        default=90,
        help="Consider files stale after N days (default: 90)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format",
    )

    args = parser.parse_args()
    sys.exit(run_stale(threshold_days=args.days, json_output=args.json))


if __name__ == "__main__":
    main()
