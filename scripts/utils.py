"""
Shared utilities for steve management scripts.

Provides common functionality for workspace analysis, component parsing,
and output formatting used across health, lint, audit, stale, and coverage scripts.
"""

import re
from pathlib import Path
from typing import Any

import yaml
from rich.console import Console
from rich.table import Table


# Constants
STEVE_DIR = "steve"
COMPONENT_DIRS = {
    "agents": "agents",
    "commands": "commands",
    "skills": "skills",
    "hooks": "hooks",
    "templates": "templates",
}

# Kebab-case pattern
KEBAB_CASE_PATTERN = re.compile(r"^[a-z][a-z0-9]*(-[a-z0-9]+)*$")

# Known tools in Claude Code
KNOWN_TOOLS = {
    "Read",
    "Write",
    "Edit",
    "MultiEdit",
    "Bash",
    "Grep",
    "Glob",
    "WebFetch",
    "WebSearch",
    "Task",
    "TodoWrite",
    "LS",
    "NotebookEdit",
    "NotebookRead",
    "AskUserQuestion",
    "SlashCommand",
    "Skill",
    "KillShell",
    "TaskOutput",
    "EnterPlanMode",
    "ExitPlanMode",
    "All tools",
    "All",
    "*",
}

# Valid agent frontmatter fields
VALID_AGENT_FIELDS = {
    "name",
    "description",
    "tools",
    "model",
    "skills",
    "color",
    "category",
    "displayName",
    "tags",
    "version",
    "author",
    "status",
    "updated",
    "tag",
    "type",
}

# Valid command frontmatter fields
VALID_COMMAND_FIELDS = {
    "name",
    "description",
    "allowed-tools",
    "argument-hint",
    "handoffs",
    "tools",
    "color",
    "category",
    "tags",
    "version",
}

# Valid hook frontmatter fields
VALID_HOOK_FIELDS = {
    "name",
    "description",
    "hooks",
    "type",
    "category",
    "version",
}

# Valid skill frontmatter fields
VALID_SKILL_FIELDS = {
    "name",
    "description",
    "author",
    "status",
    "updated",
    "version",
    "tag",
    "tags",
    "type",
    "category",
}

# Console for rich output
console = Console()


def get_repo_root() -> Path:
    """Get the repository root directory."""
    return Path(__file__).parent.parent


def get_steve_dir(repo_root: Path | None = None) -> Path:
    """Get the steve directory."""
    if repo_root is None:
        repo_root = get_repo_root()
    return repo_root / STEVE_DIR


def get_component_dir(component_type: str, repo_root: Path | None = None) -> Path:
    """Get the directory for a component type."""
    steve_dir = get_steve_dir(repo_root)
    return steve_dir / COMPONENT_DIRS.get(component_type, component_type)


def parse_frontmatter(content: str) -> tuple[dict[str, Any], str]:
    """
    Extract YAML frontmatter from markdown content.

    Args:
        content: Markdown content with potential YAML frontmatter.

    Returns:
        Tuple of (frontmatter dict, body content).
    """
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


def parse_frontmatter_file(file_path: Path) -> tuple[dict[str, Any], str]:
    """
    Parse frontmatter from a file.

    Args:
        file_path: Path to the markdown file.

    Returns:
        Tuple of (frontmatter dict, body content).
    """
    content = file_path.read_text(encoding="utf-8")
    return parse_frontmatter(content)


def is_kebab_case(name: str) -> bool:
    """Check if a name follows kebab-case convention."""
    return bool(KEBAB_CASE_PATTERN.match(name))


def get_dir_size(directory: Path) -> int:
    """
    Calculate total size of a directory in bytes.

    Args:
        directory: Path to the directory.

    Returns:
        Total size in bytes.
    """
    if not directory.exists():
        return 0

    total = 0
    try:
        for item in directory.rglob("*"):
            if item.is_file():
                try:
                    total += item.stat().st_size
                except (OSError, PermissionError):
                    continue
    except (OSError, PermissionError):
        pass

    return total


def format_size(size_bytes: int) -> str:
    """
    Format byte size into human-readable string.

    Args:
        size_bytes: Size in bytes.

    Returns:
        Formatted string like "1.5 MB".
    """
    size: float = float(size_bytes)
    for unit in ["B", "KB", "MB", "GB"]:
        if size < 1024:
            if unit == "B":
                return f"{int(size)} {unit}"
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def count_files(directory: Path, extension: str = ".md") -> int:
    """
    Count files with a given extension in a directory (recursive).

    Args:
        directory: Path to the directory.
        extension: File extension to match.

    Returns:
        Number of matching files.
    """
    if not directory.exists():
        return 0
    return len(list(directory.rglob(f"*{extension}")))


def count_dirs(directory: Path) -> int:
    """
    Count immediate subdirectories.

    Args:
        directory: Path to the directory.

    Returns:
        Number of subdirectories.
    """
    if not directory.exists():
        return 0
    return len([d for d in directory.iterdir() if d.is_dir()])


def create_table(title: str, columns: list[str]) -> Table:
    """
    Create a rich Table with standard styling.

    Args:
        title: Table title.
        columns: List of column names.

    Returns:
        Configured Table instance.
    """
    table = Table(title=title, show_header=True, header_style="bold")
    for col in columns:
        table.add_column(col)
    return table


def collect_agents(steve_dir: Path) -> list[Path]:
    """Collect all agent files."""
    agents_dir = steve_dir / "agents"
    if not agents_dir.exists():
        return []

    agents: list[Path] = []
    for domain_dir in agents_dir.iterdir():
        if domain_dir.is_dir():
            agents.extend(f for f in domain_dir.rglob("*.md") if f.name != "README.md")
    return agents


def collect_commands(steve_dir: Path) -> list[Path]:
    """Collect all command files."""
    commands_dir = steve_dir / "commands"
    if not commands_dir.exists():
        return []

    commands: list[Path] = []
    for category_dir in commands_dir.iterdir():
        if category_dir.is_dir():
            commands.extend(f for f in category_dir.rglob("*.md") if f.name != "README.md")
    return commands


def collect_skills(steve_dir: Path) -> list[tuple[Path, Path]]:
    """
    Collect all skill directories with their SKILL.md files.

    Returns:
        List of (skill_dir, skill_md_file) tuples.
    """
    skills_dir = steve_dir / "skills"
    if not skills_dir.exists():
        return []

    skills = []
    for skill_dir in skills_dir.iterdir():
        if skill_dir.is_dir():
            skill_file = skill_dir / "SKILL.md"
            if skill_file.exists():
                skills.append((skill_dir, skill_file))
    return skills


def collect_hooks(steve_dir: Path) -> list[Path]:
    """Collect all hook files."""
    hooks_dir = steve_dir / "hooks"
    if not hooks_dir.exists():
        return []

    hooks: list[Path] = []
    for hook_type_dir in hooks_dir.iterdir():
        if hook_type_dir.is_dir():
            hooks.extend(f for f in hook_type_dir.rglob("*.md") if f.name != "README.md")
    return hooks


def parse_tools_list(tools_str: str) -> list[str]:
    """
    Parse a tools string into individual tool names.

    Args:
        tools_str: Comma-separated tools string.

    Returns:
        List of tool names.
    """
    if not tools_str:
        return []

    tools = []
    for raw_tool in tools_str.split(","):
        tool_name = raw_tool.strip()
        # Skip empty, MCP tools, and bash restrictions
        if tool_name and not tool_name.startswith("mcp__") and "(" not in tool_name:
            tools.append(tool_name)
    return tools
