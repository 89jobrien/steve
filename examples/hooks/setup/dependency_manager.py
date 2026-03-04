#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml"]
# ///
"""Dependency manager for setup hooks.

Manages project dependencies:
- Detects package managers
- Checks lockfile status
- Identifies outdated dependencies
- Optionally runs install/update commands
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

import asyncio  # noqa: E402, F401, I001

from hook_logging import hook_invocation  # noqa: E402, I001
from lib.detection import PACKAGE_MANAGER_MARKERS, detect_package_manager  # noqa: E402, I001
from lib.setup import SetupReport, ValidationResult, load_setup_config  # noqa: E402, I001
from lib.subprocess import command_exists  # noqa: E402, I001


def check_lockfile(cwd: Path, package_manager: str) -> ValidationResult:
    """Check if lockfile exists for package manager.

    Args:
        cwd: Project directory
        package_manager: Package manager name

    Returns:
        ValidationResult
    """
    lockfile_map = {
        "npm": "package-lock.json",
        "yarn": "yarn.lock",
        "pnpm": "pnpm-lock.yaml",
        "bun": "bun.lockb",
        "uv": "uv.lock",
        "pip": "requirements.txt",  # Not really a lockfile but similar
        "poetry": "poetry.lock",
        "cargo": "Cargo.lock",
        "go": "go.sum",
        "bundler": "Gemfile.lock",
    }

    lockfile = lockfile_map.get(package_manager)
    if not lockfile:
        return ValidationResult(
            passed=True,
            message=f"No lockfile check for {package_manager}",
            details={"package_manager": package_manager},
            severity="info",
        )

    lockfile_path = cwd / lockfile
    if lockfile_path.exists():
        return ValidationResult(
            passed=True,
            message=f"Lockfile {lockfile} exists",
            details={"lockfile": lockfile, "exists": True},
        )

    return ValidationResult(
        passed=False,
        message=f"Lockfile {lockfile} not found",
        details={"lockfile": lockfile, "exists": False},
        severity="warning",
    )


def check_dependencies_installed(cwd: Path, package_manager: str) -> ValidationResult:
    """Check if dependencies are installed.

    Args:
        cwd: Project directory
        package_manager: Package manager name

    Returns:
        ValidationResult
    """
    install_markers = {
        "npm": "node_modules",
        "yarn": "node_modules",
        "pnpm": "node_modules",
        "bun": "node_modules",
        "uv": ".venv",
        "pip": ".venv",
        "poetry": ".venv",
        "cargo": "target",
        "go": "go.mod",  # Go modules download on demand
    }

    marker = install_markers.get(package_manager)
    if not marker:
        return ValidationResult(
            passed=True,
            message=f"Cannot check install status for {package_manager}",
            details={"package_manager": package_manager},
            severity="info",
        )

    marker_path = cwd / marker
    if marker_path.exists():
        return ValidationResult(
            passed=True,
            message=f"Dependencies appear installed ({marker} exists)",
            details={"marker": marker, "exists": True},
        )

    return ValidationResult(
        passed=False,
        message=f"Dependencies may not be installed ({marker} not found)",
        details={"marker": marker, "exists": False},
        severity="warning",
    )


async def check_outdated_deps(cwd: Path, package_manager: str) -> ValidationResult:
    """Check for outdated dependencies.

    Args:
        cwd: Project directory
        package_manager: Package manager name

    Returns:
        ValidationResult
    """
    from lib.subprocess import run_command

    outdated_cmds = {
        "npm": ["npm", "outdated", "--json"],
        "yarn": ["yarn", "outdated", "--json"],
        "pnpm": ["pnpm", "outdated", "--json"],
        "pip": ["pip", "list", "--outdated", "--format=json"],
        "uv": ["uv", "pip", "list", "--outdated", "--format=json"],
        "poetry": ["poetry", "show", "--outdated"],
        "cargo": ["cargo", "outdated", "--format=json"],
    }

    cmd = outdated_cmds.get(package_manager)
    if not cmd or not command_exists(cmd[0]):
        return ValidationResult(
            passed=True,
            message=f"Cannot check outdated deps for {package_manager}",
            details={"package_manager": package_manager},
            severity="info",
        )

    result = await run_command(cmd, cwd=cwd, timeout=30)

    if result.success:
        # Try to parse output
        try:
            if package_manager in ("npm", "yarn", "pnpm", "pip", "uv", "cargo"):
                outdated = json.loads(result.stdout)
                count = len(outdated) if isinstance(outdated, (list, dict)) else 0
                if count > 0:
                    return ValidationResult(
                        passed=False,
                        message=f"Found {count} outdated dependencies",
                        details={"count": count, "package_manager": package_manager},
                        severity="warning",
                    )
        except json.JSONDecodeError:
            pass

        return ValidationResult(
            passed=True,
            message="All dependencies up to date",
            details={"package_manager": package_manager},
        )

    return ValidationResult(
        passed=True,
        message=f"Could not check outdated deps: {result.stderr}",
        details={"error": result.stderr},
        severity="info",
    )


def validate_dependencies(
    cwd: str | Path,
    check_outdated: bool = False,
) -> SetupReport:
    """Validate project dependencies.

    Args:
        cwd: Project directory
        check_outdated: Whether to check for outdated dependencies

    Returns:
        SetupReport
    """
    report = SetupReport()
    cwd_path = Path(cwd)

    # Detect package manager
    package_manager = detect_package_manager(cwd_path)

    if not package_manager:
        report.add(
            ValidationResult(
                passed=False,
                message="No package manager detected",
                details={"supported": list(PACKAGE_MANAGER_MARKERS.keys())},
                severity="warning",
            )
        )
        return report

    report.add(
        ValidationResult(
            passed=True,
            message=f"Detected package manager: {package_manager}",
            details={"package_manager": package_manager},
        )
    )

    # Check lockfile
    result = check_lockfile(cwd_path, package_manager)
    report.add(result)

    # Check if dependencies installed
    result = check_dependencies_installed(cwd_path, package_manager)
    report.add(result)

    # Check for outdated dependencies if requested
    if check_outdated:
        result = asyncio.run(check_outdated_deps(cwd_path, package_manager))
        report.add(result)

    return report


def main() -> None:
    """Main entry point for dependency validation."""
    with hook_invocation("dependency_manager") as inv:
        try:
            payload = json.load(sys.stdin)
        except json.JSONDecodeError:
            payload = {}

        inv.set_payload(payload)

        # Load configuration
        config = load_setup_config()
        dep_config = config.get("dependency_check", {})

        # Get parameters
        cwd = payload.get("cwd", ".")
        check_outdated = payload.get("check_outdated", dep_config.get("check_vulnerabilities", False))

        # Run validation
        report = validate_dependencies(cwd, check_outdated)

        # Output report as JSON
        output = report.to_dict()
        print(json.dumps(output, indent=2))

        # Exit with appropriate code
        sys.exit(0 if report.success else 1)


if __name__ == "__main__":
    main()
