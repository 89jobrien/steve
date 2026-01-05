#!/usr/bin/env python3
"""
Security audit for the steve repository.

Scans workspace for potential security issues like exposed credentials,
sensitive files, and security best practices violations.

Usage:
    python scripts/audit.py [--json]

    --json: Output in JSON format
"""

import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

from rich.console import Console

from scripts.utils import (
    collect_agents,
    collect_commands,
    collect_hooks,
    collect_skills,
    format_size,
    get_dir_size,
    get_repo_root,
    get_steve_dir,
)


console = Console()


# Sensitive patterns to check for in files
SENSITIVE_PATTERNS = [
    ("API Key", re.compile(r"(?i)(api[_-]?key|apikey)\s*[:=]\s*['\"]?[a-zA-Z0-9_-]{20,}")),
    ("Secret", re.compile(r"(?i)(secret|password|passwd|pwd)\s*[:=]\s*['\"]?[^\s'\"]{8,}")),
    ("Token", re.compile(r"(?i)(token|bearer)\s*[:=]\s*['\"]?[a-zA-Z0-9_-]{20,}")),
    ("Private Key", re.compile(r"-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----")),
    ("AWS Key", re.compile(r"AKIA[0-9A-Z]{16}")),
    ("GitHub Token", re.compile(r"gh[pousr]_[A-Za-z0-9_]{36,}")),
    ("Slack Token", re.compile(r"xox[baprs]-[0-9]{10,13}-[0-9]{10,13}-[a-zA-Z0-9]{24}")),
]

# Sensitive files to check for
SENSITIVE_FILES = [
    ".env",
    ".env.local",
    ".env.production",
    "credentials.json",
    "secrets.yaml",
    "secrets.yml",
    "id_rsa",
    "id_ed25519",
    ".netrc",
    ".npmrc",
    ".pypirc",
]


@dataclass
class AuditIssue:
    """Represents a security issue."""

    issue_type: str
    path: str
    detail: str


@dataclass
class AuditCheck:
    """Represents a security check result."""

    name: str
    status: str  # pass, fail, warn, info
    detail: str


@dataclass
class AuditResult:
    """Result of security audit."""

    issues: list[AuditIssue] = field(default_factory=list)
    checks: list[AuditCheck] = field(default_factory=list)

    def add_issue(self, issue_type: str, path: str, detail: str) -> None:
        """Add a security issue."""
        self.issues.append(AuditIssue(issue_type, path, detail))

    def add_check(self, name: str, status: str, detail: str) -> None:
        """Add a check result."""
        self.checks.append(AuditCheck(name, status, detail))

    @property
    def pass_count(self) -> int:
        """Count of passed checks."""
        return sum(1 for c in self.checks if c.status == "pass")

    @property
    def score(self) -> float:
        """Calculate security score as percentage."""
        if not self.checks:
            return 100.0
        return (self.pass_count / len(self.checks)) * 100


def check_sensitive_files(repo_root: Path, result: AuditResult) -> None:
    """Check for sensitive files in the repository."""
    found_files = []

    for sensitive_file in SENSITIVE_FILES:
        file_path = repo_root / sensitive_file
        if file_path.exists():
            found_files.append(sensitive_file)
            result.add_issue(
                "sensitive_file",
                sensitive_file,
                "Sensitive file found in repository",
            )

    if found_files:
        result.add_check(
            "Sensitive Files",
            "fail",
            f"{len(found_files)} sensitive files found",
        )
    else:
        result.add_check(
            "Sensitive Files",
            "pass",
            "No sensitive files found",
        )


def scan_for_secrets(steve_dir: Path, result: AuditResult) -> None:
    """Scan markdown files for potential secrets."""
    secrets_found = 0
    files_to_scan: list[Path] = []

    # Collect all component files
    files_to_scan.extend(collect_agents(steve_dir))
    files_to_scan.extend(collect_commands(steve_dir))
    files_to_scan.extend(collect_hooks(steve_dir))
    for _, skill_file in collect_skills(steve_dir):
        files_to_scan.append(skill_file)

    for file_path in files_to_scan:
        try:
            content = file_path.read_text(encoding="utf-8")
            rel_path = str(file_path.relative_to(steve_dir))

            for pattern_name, pattern in SENSITIVE_PATTERNS:
                if pattern.search(content):
                    secrets_found += 1
                    result.add_issue(
                        "secret_pattern",
                        rel_path,
                        f"Potential {pattern_name} detected",
                    )
        except (OSError, UnicodeDecodeError):
            continue

    if secrets_found == 0:
        result.add_check(
            "Secret Patterns",
            "pass",
            "No secrets detected in component files",
        )
    else:
        result.add_check(
            "Secret Patterns",
            "warn",
            f"{secrets_found} potential secrets found",
        )


def check_file_permissions(repo_root: Path, result: AuditResult) -> None:
    """Check for world-readable/writable files."""
    perm_issues = 0

    for file_path in repo_root.rglob("*"):
        if file_path.is_file():
            try:
                mode = file_path.stat().st_mode
                # Check for world-readable/writable (others have access)
                if mode & 0o007:
                    perm_issues += 1
            except (OSError, PermissionError):
                continue

    if perm_issues == 0:
        result.add_check(
            "File Permissions",
            "pass",
            "No world-accessible files",
        )
    else:
        result.add_check(
            "File Permissions",
            "info",
            f"{perm_issues} files with world access",
        )


def check_large_directories(steve_dir: Path, result: AuditResult) -> None:
    """Check for unusually large directories."""
    threshold_mb = 50

    for dir_name in ["agents", "commands", "skills", "hooks"]:
        dir_path = steve_dir / dir_name
        if dir_path.exists():
            size_bytes = get_dir_size(dir_path)
            size_mb = size_bytes / (1024 * 1024)

            if size_mb > threshold_mb:
                result.add_check(
                    f"{dir_name.capitalize()} Size",
                    "warn",
                    f"Directory is {size_mb:.1f}MB (recommend cleanup)",
                )
            else:
                result.add_check(
                    f"{dir_name.capitalize()} Size",
                    "pass",
                    f"Directory is {format_size(size_bytes)}",
                )


def check_gitignore(repo_root: Path, result: AuditResult) -> None:
    """Check if .gitignore exists and covers sensitive patterns."""
    gitignore_path = repo_root / ".gitignore"

    if not gitignore_path.exists():
        result.add_check(
            "Gitignore",
            "warn",
            "No .gitignore file found",
        )
        return

    content = gitignore_path.read_text(encoding="utf-8")
    recommended = [".env", "*.local", "secrets"]
    missing = [p for p in recommended if p not in content]

    if missing:
        result.add_check(
            "Gitignore",
            "info",
            f"Consider adding: {', '.join(missing)}",
        )
    else:
        result.add_check(
            "Gitignore",
            "pass",
            "Gitignore covers common sensitive patterns",
        )


def run_audit(json_output: bool = False) -> int:
    """Run the security audit and display results."""
    repo_root = get_repo_root()
    steve_dir = get_steve_dir(repo_root)

    if not steve_dir.exists():
        console.print("[red]Error: steve directory not found[/red]")
        return 1

    result = AuditResult()

    # Run all checks
    check_sensitive_files(repo_root, result)
    scan_for_secrets(steve_dir, result)
    check_file_permissions(repo_root, result)
    check_large_directories(steve_dir, result)
    check_gitignore(repo_root, result)

    if json_output:
        output = {
            "workspace": "steve",
            "issues": [
                {
                    "type": i.issue_type,
                    "path": i.path,
                    "detail": i.detail,
                }
                for i in result.issues
            ],
            "checks": [
                {
                    "name": c.name,
                    "status": c.status,
                    "detail": c.detail,
                }
                for c in result.checks
            ],
            "score": round(result.score),
        }
        print(json.dumps(output, indent=2))
        return 0 if result.score >= 70 else 1

    # Rich output
    console.print()
    console.print("[bold cyan]Security Audit: steve[/bold cyan]")
    console.print(f"[dim]{repo_root}[/dim]")
    console.print()

    console.print("[bold]Security Checks:[/bold]")
    for check in result.checks:
        if check.status == "pass":
            status_icon = "[green]OK[/green]"
        elif check.status == "fail":
            status_icon = "[red]X[/red]"
        elif check.status == "warn":
            status_icon = "[yellow]![/yellow]"
        else:
            status_icon = "[blue]i[/blue]"

        console.print(f"  {status_icon} {check.name}")
        console.print(f"      [dim]{check.detail}[/dim]")
    console.print()

    if result.issues:
        console.print("[bold]Issues Found:[/bold]")
        for issue in result.issues:
            console.print(f"  [yellow]![/yellow] {issue.path}: {issue.detail}")
        console.print()

    # Security score
    console.print(
        f"Security Score: [bold]{result.score:.0f}%[/bold] "
        f"({result.pass_count}/{len(result.checks)} checks passed)"
    )

    return 0 if result.score >= 70 else 1


def main() -> None:
    """Entry point for the audit command."""
    parser = argparse.ArgumentParser(description="Run security audit on steve repository")
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output in JSON format",
    )

    args = parser.parse_args()
    sys.exit(run_audit(json_output=args.json))


if __name__ == "__main__":
    main()
