#!/usr/bin/env python3
"""
Tool coverage analysis for the steve repository.

Analyzes which tools are used across agents, showing usage statistics
and identifying potentially underutilized tools.

Usage:
    python scripts/coverage.py [--json]

    --json: Output in JSON format
"""

import argparse
import json
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

from rich.console import Console
from rich.table import Table

from scripts.utils import (
    KNOWN_TOOLS,
    collect_agents,
    get_repo_root,
    get_steve_dir,
    parse_frontmatter_file,
    parse_tools_list,
)


console = Console()


@dataclass
class ToolUsage:
    """Tracks tool usage across agents."""

    tool_counts: Counter = field(default_factory=Counter)
    tool_agents: dict[str, list[str]] = field(default_factory=dict)
    total_agents: int = 0

    def add_agent(self, agent_name: str, tools: list[str]) -> None:
        """Record tool usage for an agent."""
        self.total_agents += 1
        for tool in tools:
            self.tool_counts[tool] += 1
            self.tool_agents.setdefault(tool, []).append(agent_name)

    def get_usage_percent(self, tool: str) -> float:
        """Get percentage of agents using a tool."""
        if self.total_agents == 0:
            return 0.0
        return (self.tool_counts[tool] / self.total_agents) * 100


def analyze_tool_coverage(steve_dir: Path) -> ToolUsage:
    """Analyze tool usage across all agents."""
    usage = ToolUsage()

    for agent_file in collect_agents(steve_dir):
        try:
            frontmatter, _ = parse_frontmatter_file(agent_file)
            agent_name = agent_file.stem

            tools_value = frontmatter.get("tools", "")

            # Handle tools being either a string or list
            if isinstance(tools_value, list):
                tools_str = ", ".join(str(t) for t in tools_value)
            else:
                tools_str = str(tools_value) if tools_value else ""

            # Skip "All tools" type entries
            if tools_str.lower() in ("all tools", "all", "*"):
                usage.add_agent(agent_name, ["All tools"])
                continue

            tools = parse_tools_list(tools_str)
            if tools:
                usage.add_agent(agent_name, tools)
            else:
                usage.add_agent(agent_name, [])

        except (OSError, UnicodeDecodeError):
            continue

    return usage


def run_coverage(json_output: bool = False) -> int:
    """Run the coverage analysis and display results."""
    repo_root = get_repo_root()
    steve_dir = get_steve_dir(repo_root)

    if not steve_dir.exists():
        console.print("[red]Error: steve directory not found[/red]")
        return 1

    usage = analyze_tool_coverage(steve_dir)

    if json_output:
        # Build sorted tool list
        tool_data = []
        for tool, count in usage.tool_counts.most_common():
            tool_data.append(
                {
                    "tool": tool,
                    "count": count,
                    "percent": round(usage.get_usage_percent(tool), 1),
                    "agents": usage.tool_agents.get(tool, []),
                }
            )

        # Find unused known tools
        used_tools = set(usage.tool_counts.keys())
        base_known = {t for t in KNOWN_TOOLS if t not in ("All tools", "All", "*")}
        unused = sorted(base_known - used_tools)

        output = {
            "workspace": "steve",
            "total_agents": usage.total_agents,
            "tools": tool_data,
            "unused_known_tools": unused,
        }
        print(json.dumps(output, indent=2))
        return 0

    # Rich output
    console.print()
    console.print("[bold cyan]Tool Coverage Analysis[/bold cyan]")
    console.print(f"[dim]Analyzed {usage.total_agents} agents[/dim]")
    console.print()

    if not usage.tool_counts:
        console.print("[yellow]No tool usage found[/yellow]")
        return 0

    # Most used tools table
    table = Table(
        title="Tool Usage",
        show_header=True,
        header_style="bold",
    )
    table.add_column("Tool", style="cyan")
    table.add_column("Count", justify="right")
    table.add_column("Usage", justify="right")
    table.add_column("Bar")

    max_count = max(usage.tool_counts.values()) if usage.tool_counts else 1

    for tool, count in usage.tool_counts.most_common():
        percent = usage.get_usage_percent(tool)
        bar_width = int((count / max_count) * 20)
        bar = "[green]" + "|" * bar_width + "[/green]"
        table.add_row(tool, str(count), f"{percent:.0f}%", bar)

    console.print(table)
    console.print()

    # Single-use tools
    single_use = [t for t, c in usage.tool_counts.items() if c == 1]
    if single_use:
        console.print("[bold]Single-Use Tools:[/bold]")
        for tool in sorted(single_use):
            agents = usage.tool_agents.get(tool, [])
            agent_str = agents[0] if agents else "unknown"
            console.print(f"  [dim]{tool}[/dim] -> {agent_str}")
        console.print()

    # Unused known tools
    used_tools = set(usage.tool_counts.keys())
    base_known = {t for t in KNOWN_TOOLS if t not in ("All tools", "All", "*")}
    unused = sorted(base_known - used_tools)

    if unused:
        console.print("[bold]Unused Known Tools:[/bold]")
        console.print(f"  [dim]{', '.join(unused)}[/dim]")
        console.print()

    # Summary
    console.print(
        f"[bold]{len(usage.tool_counts)}[/bold] unique tools used across "
        f"[bold]{usage.total_agents}[/bold] agents"
    )

    return 0


def main() -> None:
    """Entry point for the coverage command."""
    parser = argparse.ArgumentParser(description="Analyze tool coverage across steve agents")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format",
    )

    args = parser.parse_args()
    sys.exit(run_coverage(json_output=args.json))


if __name__ == "__main__":
    main()
