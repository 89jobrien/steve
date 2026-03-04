#!/usr/bin/env python3
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""
Generate README.md from component frontmatter.

Usage:
    uv run scripts/generate_readme.py [--check] [--output FILE]

Options:
    --check     Check if README is up-to-date (exit 1 if not)
    --output    Output file (default: README.md)
"""

import argparse
import sys
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Agent:
    name: str
    description: str
    tools: str
    skills: str
    category: str
    file_path: Path


@dataclass
class Command:
    name: str
    description: str
    category: str
    file_path: Path


@dataclass
class Skill:
    name: str
    description: str
    file_path: Path


def parse_frontmatter(content: str) -> dict[str, str]:
    """Extract YAML frontmatter from markdown file."""
    if not content.startswith("---"):
        return {}

    # Find the closing ---
    parts = content.split("---", 2)
    if len(parts) < 3:
        return {}

    frontmatter = parts[1].strip()
    result = {}

    # Simple YAML parser for our use case
    for line in frontmatter.split("\n"):
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        # Handle simple key: value
        if ":" in line and not line.startswith(" "):
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip().strip('"').strip("'")

    return result


def scan_agents(base_path: Path) -> list[Agent]:
    """Scan all agent markdown files and extract metadata."""
    agents = []
    agents_dir = base_path / "agents"

    for agent_file in agents_dir.rglob("*.md"):
        if agent_file.parent == agents_dir:
            continue  # Skip files directly in agents/

        category = agent_file.parent.name
        content = agent_file.read_text(encoding="utf-8")
        fm = parse_frontmatter(content)

        if "name" not in fm:
            continue

        agents.append(
            Agent(
                name=fm.get("name", ""),
                description=fm.get("description", ""),
                tools=fm.get("tools", "-"),
                skills=fm.get("skills", "-"),
                category=category,
                file_path=agent_file,
            )
        )

    return sorted(agents, key=lambda a: a.name)


def scan_commands(base_path: Path) -> list[Command]:
    """Scan all command markdown files and extract metadata."""
    commands = []
    commands_dir = base_path / "commands"

    for cmd_file in commands_dir.rglob("*.md"):
        if cmd_file.parent == commands_dir:
            continue  # Skip files directly in commands/

        category = cmd_file.parent.name
        content = cmd_file.read_text(encoding="utf-8")
        fm = parse_frontmatter(content)

        if "description" not in fm:
            continue

        # Get command name from filename
        name = cmd_file.stem

        commands.append(
            Command(
                name=name,
                description=fm.get("description", ""),
                category=category,
                file_path=cmd_file,
            )
        )

    return sorted(commands, key=lambda c: c.name)


def scan_skills(base_path: Path) -> list[Skill]:
    """Scan all skill SKILL.md files and extract metadata."""
    skills = []
    skills_dir = base_path / "skills"

    for skill_file in skills_dir.glob("*/SKILL.md"):
        content = skill_file.read_text(encoding="utf-8")
        fm = parse_frontmatter(content)

        if "name" not in fm:
            continue

        skills.append(
            Skill(
                name=fm.get("name", ""),
                description=fm.get("description", ""),
                file_path=skill_file,
            )
        )

    return sorted(skills, key=lambda s: s.name)


def categorize_agents(agents: list[Agent]) -> dict[str, list[Agent]]:
    """Group agents by category."""
    categories = defaultdict(list)
    for agent in agents:
        categories[agent.category].append(agent)
    return dict(categories)


def categorize_commands(commands: list[Command]) -> dict[str, list[Command]]:
    """Group commands by category."""
    categories = defaultdict(list)
    for cmd in commands:
        categories[cmd.category].append(cmd)
    return dict(categories)


def format_category_name(category: str) -> str:
    """Convert kebab-case to Title Case."""
    return category.replace("-", " ").replace("_", " ").title()


def truncate_description(desc: str, max_length: int = 120) -> str:
    """Truncate description to max_length, adding ellipsis if needed."""
    if len(desc) <= max_length:
        return desc
    return desc[: max_length - 3] + "..."


def generate_readme(base_path: Path) -> str:
    """Generate complete README content."""
    agents = scan_agents(base_path)
    commands = scan_commands(base_path)
    skills = scan_skills(base_path)

    agent_categories = categorize_agents(agents)
    command_categories = categorize_commands(commands)

    # Start with static header content
    content = """# Claude Workspace Index

## Core Sets

### Core Agents
- code-reviewer
- test-engineer
- architect-reviewer
- performance-engineer
- security-engineer
- logging-specialist
- tdd-orchestrator
- test-automator
- backend-architect
- research-expert
- debugger
- valerie

### Core Skills
- testing
- tdd-pytest
- documentation
- performance
- database-optimization
- security-engineering
- security-audit
- debugging
- tool-presets
- lead-research-assistant
- context-management
- command-optimization

---

## Stats & health

make stats              # Component counts
make health             # Full health check
make validate           # Validate all components

## Code quality

make lint               # Lint Python with ruff
make format             # Format Python with ruff

## Search

make find-agent NAME=database
make grep-all PATTERN=performance

## Create new components

make new-agent NAME=my-agent CATEGORY=testing
make new-skill NAME=my-skill
make new-command NAME=my-cmd CATEGORY=dev

## Maintenance

make cleanup            # Remove caches
make cleanup-debug      # Clean debug dir

---

## Scripts

### Validate all components

~/.claude/scripts/validate-components.sh

### Search components

~/.claude/scripts/search-components.sh "database"
~/.claude/scripts/search-components.sh "test" agents

---

Comprehensive index of all agents, commands, and skills.

## Agents

"""

    # Generate agent sections
    for category in sorted(agent_categories.keys()):
        category_agents = agent_categories[category]
        content += f"### {format_category_name(category)}\n\n"

        for agent in category_agents:
            desc = truncate_description(agent.description)
            content += f"- **{agent.name}**: {desc} | Tools: {agent.tools} | Skills: {agent.skills}\n"

        content += "\n"

    # Generate commands section
    content += "## Commands\n\n"

    for category in sorted(command_categories.keys()):
        category_commands = command_categories[category]
        content += f"### {format_category_name(category)}\n\n"

        for cmd in category_commands:
            desc = truncate_description(cmd.description)
            content += f"- **/{category}:{cmd.name}**: {desc}\n"

        content += "\n"

    # Generate skills section
    content += "## Skills\n\n"

    for skill in skills:
        desc = truncate_description(skill.description, max_length=100)
        # Find which agents use this skill
        using_agents = [a.name for a in agents if skill.name in a.skills.split(", ")]
        used_by = f" | Used by: {', '.join(using_agents[:5])}" if using_agents else ""
        content += f"- **{skill.name}**: {desc}{used_by}\n"

    content += "\n"

    # Add footer
    agent_count = len(agents)
    command_count = len(commands)
    skill_count = len(skills)

    content += f"""---

**Total Components:**
- Agents: {agent_count}
- Commands: {command_count}
- Skills: {skill_count}

**Auto-generated** by `scripts/generate_readme.py`
"""

    return content


def main():
    parser = argparse.ArgumentParser(description="Generate README from components")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check if README is up-to-date (exit 1 if not)",
    )
    parser.add_argument(
        "--output", default="README.md", help="Output file (default: README.md)"
    )

    args = parser.parse_args()

    # Find claude directory
    claude_dir = Path.home() / ".claude"
    if not claude_dir.exists():
        print(f"Error: {claude_dir} does not exist", file=sys.stderr)
        sys.exit(1)

    # Generate README content
    print("Scanning components...")
    content = generate_readme(claude_dir)

    output_path = claude_dir / args.output

    if args.check:
        # Check if current README matches generated content
        if not output_path.exists():
            print(f"README does not exist: {output_path}", file=sys.stderr)
            sys.exit(1)

        current = output_path.read_text(encoding="utf-8")
        if current != content:
            print("README is out of date. Run without --check to update.", file=sys.stderr)
            sys.exit(1)

        print("README is up to date.")
        sys.exit(0)

    # Write README
    output_path.write_text(content, encoding="utf-8")
    print(f"Generated {output_path}")

    # Show stats
    agents = scan_agents(claude_dir)
    commands = scan_commands(claude_dir)
    skills = scan_skills(claude_dir)

    print("\nComponents indexed:")
    print(f"  - Agents: {len(agents)}")
    print(f"  - Commands: {len(commands)}")
    print(f"  - Skills: {len(skills)}")


if __name__ == "__main__":
    main()
