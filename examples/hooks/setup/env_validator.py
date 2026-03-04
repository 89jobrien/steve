#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml"]
# ///
"""Environment validator for setup hooks.

Validates development environment:
- Required tools and binaries
- Tool versions
- Environment variables
- PATH configuration
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from hook_logging import hook_invocation  # noqa: E402, I001
from lib.setup import (  # noqa: E402, I001
    SetupReport,
    ValidationResult,
    check_env_var,
    load_setup_config,
)
from lib.subprocess import command_exists  # noqa: E402, I001


def parse_version(version_str: str) -> tuple[int, ...]:
    """Parse version string into tuple of ints.

    Args:
        version_str: Version string like "3.12.0" or "v18.0.0"

    Returns:
        Tuple of version numbers
    """
    # Remove leading 'v' if present
    version_str = version_str.lstrip("v")

    # Extract numeric parts
    match = re.match(r"(\d+)\.(\d+)(?:\.(\d+))?", version_str)
    if not match:
        return (0,)

    parts = match.groups()
    return tuple(int(p) for p in parts if p is not None)


def compare_versions(actual: str, required: str) -> bool:
    """Compare if actual version meets required version.

    Args:
        actual: Actual version string
        required: Required version string (supports >=, >, =)

    Returns:
        True if version requirement is met
    """
    # Parse operator and version
    op = ">="
    if required.startswith(">="):
        op = ">="
        required = required[2:].strip()
    elif required.startswith(">"):
        op = ">"
        required = required[1:].strip()
    elif required.startswith("="):
        op = "="
        required = required[1:].strip()

    actual_ver = parse_version(actual)
    required_ver = parse_version(required)

    if op == ">=":
        return actual_ver >= required_ver
    if op == ">":
        return actual_ver > required_ver
    if op == "=":
        return actual_ver == required_ver

    return False


def get_tool_version(tool: str) -> str | None:
    """Get version of a tool.

    Args:
        tool: Tool name

    Returns:
        Version string or None if not found
    """
    version_cmds = {
        "git": ["git", "--version"],
        "node": ["node", "--version"],
        "npm": ["npm", "--version"],
        "python": ["python3", "--version"],
        "python3": ["python3", "--version"],
        "docker": ["docker", "--version"],
        "go": ["go", "version"],
        "rust": ["rustc", "--version"],
        "cargo": ["cargo", "--version"],
        "uv": ["uv", "--version"],
    }

    cmd = version_cmds.get(tool, [tool, "--version"])

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            # Extract version from output
            output = result.stdout.strip()
            # Look for version pattern
            match = re.search(r"v?(\d+\.\d+(?:\.\d+)?)", output)
            if match:
                return match.group(1)
            return output
    except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
        pass

    return None


def check_tool(tool: str, version_req: str | None = None) -> ValidationResult:
    """Check if a tool exists and optionally check version.

    Args:
        tool: Tool name
        version_req: Optional version requirement (e.g., ">=3.12")

    Returns:
        ValidationResult
    """
    if not command_exists(tool):
        return ValidationResult(
            passed=False,
            message=f"Tool '{tool}' not found",
            details={"tool": tool, "available": False},
            severity="error",
        )

    # Get version if requirement specified
    if version_req:
        version = get_tool_version(tool)
        if not version:
            return ValidationResult(
                passed=False,
                message=f"Tool '{tool}' found but version could not be determined",
                details={"tool": tool, "version_required": version_req},
                severity="warning",
            )

        if compare_versions(version, version_req):
            return ValidationResult(
                passed=True,
                message=f"Tool '{tool}' version {version} meets requirement {version_req}",
                details={"tool": tool, "version": version, "required": version_req},
            )
        return ValidationResult(
            passed=False,
            message=f"Tool '{tool}' version {version} does not meet requirement {version_req}",
            details={"tool": tool, "version": version, "required": version_req},
            severity="error",
        )

    # Tool exists, no version check
    version = get_tool_version(tool)
    return ValidationResult(
        passed=True,
        message=f"Tool '{tool}' is available" + (f" (version {version})" if version else ""),
        details={"tool": tool, "version": version, "available": True},
    )


def validate_environment(
    required_tools: list[str | dict] | None = None,
    required_env_vars: list[str] | None = None,
) -> SetupReport:
    """Validate development environment.

    Args:
        required_tools: List of tools to check (can be strings or dicts with version)
        required_env_vars: List of environment variables to check

    Returns:
        SetupReport with validation results
    """
    report = SetupReport()

    # Check tools
    if required_tools:
        for tool_spec in required_tools:
            if isinstance(tool_spec, str):
                # Simple tool name
                if ":" in tool_spec:
                    # Format: "tool:>=version"
                    tool, version = tool_spec.split(":", 1)
                    result = check_tool(tool.strip(), version.strip())
                else:
                    result = check_tool(tool_spec)
            elif isinstance(tool_spec, dict):
                # Dict format: {"name": "python3", "version": ">=3.12"}
                tool = tool_spec.get("name", "")
                version = tool_spec.get("version")
                result = check_tool(tool, version)
            else:
                continue

            report.add(result)

    # Check environment variables
    if required_env_vars:
        for env_var in required_env_vars:
            result = check_env_var(env_var)
            report.add(result)

    return report


def main() -> None:
    """Main entry point for environment validation."""
    with hook_invocation("env_validator") as inv:
        try:
            payload = json.load(sys.stdin)
        except json.JSONDecodeError:
            payload = {}

        inv.set_payload(payload)

        # Load configuration
        config = load_setup_config()
        env_config = config.get("env_validation", {})

        # Get required tools and env vars from config or payload
        required_tools = payload.get("required_tools") or env_config.get("required_tools", [])
        required_env_vars = payload.get("required_env_vars") or env_config.get("required_env_vars", [])

        # Run validation
        report = validate_environment(required_tools, required_env_vars)

        # Output report as JSON
        output = report.to_dict()
        print(json.dumps(output, indent=2))

        # Exit with appropriate code
        sys.exit(0 if report.success else 1)


if __name__ == "__main__":
    main()
