#!/usr/bin/env python3
"""
Component linter for the steve repository.

Checks workspace components for quality issues, missing fields,
and adherence to best practices.

Usage:
    python scripts/lint.py [--json] [--errors-only]

    --json: Output in JSON format
    --errors-only: Only show errors, not warnings
"""

import argparse
import json
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path

from rich.console import Console

from scripts.utils import (
    KNOWN_TOOLS,
    VALID_AGENT_FIELDS,
    VALID_COMMAND_FIELDS,
    VALID_HOOK_FIELDS,
    VALID_SKILL_FIELDS,
    collect_agents,
    collect_commands,
    collect_hooks,
    collect_skills,
    get_repo_root,
    get_steve_dir,
    is_kebab_case,
    parse_frontmatter_file,
    parse_tools_list,
)


console = Console()


class Severity(str, Enum):
    """Lint issue severity."""

    ERROR = "error"
    WARNING = "warning"


@dataclass
class LintIssue:
    """Represents a lint issue."""

    rule: str
    path: str
    detail: str
    severity: Severity


@dataclass
class LintResult:
    """Result of linting operation."""

    issues: list[LintIssue] = field(default_factory=list)

    @property
    def error_count(self) -> int:
        """Count of error-level issues."""
        return sum(1 for i in self.issues if i.severity == Severity.ERROR)

    @property
    def warning_count(self) -> int:
        """Count of warning-level issues."""
        return sum(1 for i in self.issues if i.severity == Severity.WARNING)

    def add(self, rule: str, path: str, detail: str, severity: Severity = Severity.ERROR) -> None:
        """Add an issue to the result."""
        self.issues.append(LintIssue(rule, path, detail, severity))


def lint_agent(file_path: Path, steve_dir: Path, result: LintResult) -> None:
    """Lint an agent file."""
    rel_path = str(file_path.relative_to(steve_dir))
    filename = file_path.stem

    try:
        frontmatter, _ = parse_frontmatter_file(file_path)
    except Exception as e:
        result.add("frontmatter-invalid", rel_path, str(e))
        return

    if not frontmatter:
        result.add("frontmatter-missing", rel_path, "File has no frontmatter")
        return

    # Required fields
    if not frontmatter.get("name"):
        result.add("agent-name-required", rel_path, "Missing 'name' field")

    if not frontmatter.get("description"):
        result.add("agent-description-required", rel_path, "Missing 'description' field")

    if not frontmatter.get("tools"):
        result.add("agent-tools-required", rel_path, "Missing 'tools' field")

    # Recommended fields
    if not frontmatter.get("model"):
        result.add(
            "agent-model-recommended",
            rel_path,
            "Consider adding 'model' field",
            Severity.WARNING,
        )

    # Name mismatch
    name = frontmatter.get("name", "")
    if name and name != filename:
        normalized = name.lower().replace(" ", "-")
        if normalized != filename:
            result.add(
                "name-mismatch",
                rel_path,
                f"name '{name}' != filename '{filename}'",
                Severity.WARNING,
            )

    # Validate tools
    tools_value = frontmatter.get("tools", "")
    # Handle tools being either a string or list
    if isinstance(tools_value, list):
        tools_str = ", ".join(str(t) for t in tools_value)
    else:
        tools_str = str(tools_value) if tools_value else ""

    if tools_str and tools_str.lower() not in ("all tools", "all", "*"):
        for tool_name in parse_tools_list(tools_str):
            if tool_name not in KNOWN_TOOLS:
                result.add(
                    "agent-unknown-tool",
                    rel_path,
                    f"Unknown tool: {tool_name}",
                    Severity.WARNING,
                )

    # Check for skills that don't exist
    skills_str = frontmatter.get("skills", "")
    if skills_str:
        skills_dir = steve_dir / "skills"
        for raw_skill in skills_str.split(","):
            skill_name = raw_skill.strip()
            if skill_name and not (skills_dir / skill_name).exists():
                result.add(
                    "agent-missing-skill",
                    rel_path,
                    f"Skill not found: {skill_name}",
                    Severity.WARNING,
                )

    # Unknown fields
    for field_name in frontmatter:
        if field_name not in VALID_AGENT_FIELDS:
            result.add(
                "frontmatter-unknown-field",
                rel_path,
                f"Unknown field: {field_name}",
                Severity.WARNING,
            )

    # Kebab-case filename
    if not is_kebab_case(filename):
        result.add(
            "file-not-kebab-case",
            rel_path,
            f"'{filename}' should be kebab-case",
            Severity.WARNING,
        )


def lint_command(file_path: Path, steve_dir: Path, result: LintResult) -> None:
    """Lint a command file."""
    rel_path = str(file_path.relative_to(steve_dir))
    filename = file_path.stem

    try:
        frontmatter, _ = parse_frontmatter_file(file_path)
    except Exception as e:
        result.add("frontmatter-invalid", rel_path, str(e))
        return

    if not frontmatter:
        result.add("frontmatter-missing", rel_path, "File has no frontmatter")
        return

    # Required fields
    if not frontmatter.get("description"):
        result.add("command-description-required", rel_path, "Missing 'description' field")

    # Recommended fields
    if "allowed-tools" not in frontmatter:
        result.add(
            "command-allowed-tools-recommended",
            rel_path,
            "Consider adding 'allowed-tools' field",
            Severity.WARNING,
        )

    # Unknown fields
    for field_name in frontmatter:
        if field_name not in VALID_COMMAND_FIELDS:
            result.add(
                "frontmatter-unknown-field",
                rel_path,
                f"Unknown field: {field_name}",
                Severity.WARNING,
            )

    # Kebab-case filename
    if not is_kebab_case(filename):
        result.add(
            "file-not-kebab-case",
            rel_path,
            f"'{filename}' should be kebab-case",
            Severity.WARNING,
        )


def lint_hook(file_path: Path, steve_dir: Path, result: LintResult) -> None:
    """Lint a hook file."""
    rel_path = str(file_path.relative_to(steve_dir))
    filename = file_path.stem

    try:
        frontmatter, _ = parse_frontmatter_file(file_path)
    except Exception as e:
        result.add("frontmatter-invalid", rel_path, str(e))
        return

    if not frontmatter:
        result.add("frontmatter-missing", rel_path, "File has no frontmatter")
        return

    # Required fields
    if not frontmatter.get("name"):
        result.add("hook-name-required", rel_path, "Missing 'name' field")

    if not frontmatter.get("description"):
        result.add("hook-description-required", rel_path, "Missing 'description' field")

    # Unknown fields
    for field_name in frontmatter:
        if field_name not in VALID_HOOK_FIELDS:
            result.add(
                "frontmatter-unknown-field",
                rel_path,
                f"Unknown field: {field_name}",
                Severity.WARNING,
            )

    # Kebab-case filename
    if not is_kebab_case(filename):
        result.add(
            "file-not-kebab-case",
            rel_path,
            f"'{filename}' should be kebab-case",
            Severity.WARNING,
        )


def lint_skill(skill_dir: Path, skill_file: Path, steve_dir: Path, result: LintResult) -> None:
    """Lint a skill directory."""
    rel_path = str(skill_dir.relative_to(steve_dir))

    try:
        frontmatter, _ = parse_frontmatter_file(skill_file)
    except Exception as e:
        result.add("frontmatter-invalid", rel_path, str(e))
        return

    if not frontmatter:
        result.add("frontmatter-missing", rel_path, "SKILL.md has no frontmatter")
        return

    # Required fields
    if not frontmatter.get("name"):
        result.add("skill-name-required", rel_path, "Missing 'name' field")

    if not frontmatter.get("description"):
        result.add(
            "skill-empty-description",
            rel_path,
            "SKILL.md has no description",
            Severity.WARNING,
        )

    # Unknown fields
    for field_name in frontmatter:
        if field_name not in VALID_SKILL_FIELDS:
            result.add(
                "frontmatter-unknown-field",
                rel_path,
                f"Unknown field: {field_name}",
                Severity.WARNING,
            )

    # Kebab-case directory name
    dir_name = skill_dir.name
    if not is_kebab_case(dir_name):
        result.add(
            "file-not-kebab-case",
            rel_path,
            f"'{dir_name}' should be kebab-case",
            Severity.WARNING,
        )


def run_lint(json_output: bool = False, errors_only: bool = False) -> int:
    """Run the linter and display results."""
    repo_root = get_repo_root()
    steve_dir = get_steve_dir(repo_root)

    if not steve_dir.exists():
        console.print("[red]Error: steve directory not found[/red]")
        return 1

    result = LintResult()

    # Lint agents
    for agent_file in collect_agents(steve_dir):
        lint_agent(agent_file, steve_dir, result)

    # Lint commands
    for command_file in collect_commands(steve_dir):
        lint_command(command_file, steve_dir, result)

    # Lint hooks
    for hook_file in collect_hooks(steve_dir):
        lint_hook(hook_file, steve_dir, result)

    # Lint skills
    for skill_dir, skill_file in collect_skills(steve_dir):
        lint_skill(skill_dir, skill_file, steve_dir, result)

    if json_output:
        issues = result.issues
        if errors_only:
            issues = [i for i in issues if i.severity == Severity.ERROR]

        output = {
            "workspace": "steve",
            "issues": [
                {
                    "rule": i.rule,
                    "path": i.path,
                    "detail": i.detail,
                    "severity": i.severity.value,
                }
                for i in issues
            ],
            "summary": {
                "errors": result.error_count,
                "warnings": result.warning_count,
            },
        }
        print(json.dumps(output, indent=2))
        return 1 if result.error_count > 0 else 0

    # Rich output
    console.print()
    console.print("[bold cyan]Steve Component Linter[/bold cyan]")
    console.print(f"[dim]{steve_dir}[/dim]")
    console.print()

    if not result.issues:
        console.print("[green]No issues found[/green]")
        return 0

    # Group by severity
    errors = [i for i in result.issues if i.severity == Severity.ERROR]
    warnings = [i for i in result.issues if i.severity == Severity.WARNING]

    if errors:
        console.print(f"[bold red]Errors ({len(errors)})[/bold red]")
        for issue in errors:
            console.print(f"  [red]X[/red] {issue.path}")
            console.print(f"      {issue.rule}: {issue.detail}")
        console.print()

    if warnings and not errors_only:
        console.print(f"[bold yellow]Warnings ({len(warnings)})[/bold yellow]")
        for issue in warnings:
            console.print(f"  [yellow]![/yellow] {issue.path}")
            console.print(f"      {issue.rule}: {issue.detail}")
        console.print()

    # Summary
    console.print(f"Found {result.error_count} errors and {result.warning_count} warnings")

    return 1 if result.error_count > 0 else 0


def main() -> None:
    """Entry point for the lint command."""
    parser = argparse.ArgumentParser(description="Lint steve components for quality issues")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format",
    )
    parser.add_argument(
        "--errors-only",
        action="store_true",
        help="Only show errors, not warnings",
    )

    args = parser.parse_args()
    sys.exit(run_lint(json_output=args.json, errors_only=args.errors_only))


if __name__ == "__main__":
    main()
