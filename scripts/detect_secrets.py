#!/usr/bin/env python3
"""
Secrets detection script for the steve repository.

Scans repository for potential secrets and sensitive information.
Uses detect-secrets library for comprehensive scanning.

Usage:
    python scripts/detect_secrets.py [--baseline] [--scan]

    --baseline: Generate/update .secrets.baseline
    --scan: Scan repository and report findings
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], check: bool = True) -> tuple[str, str, int]:
    """Run a command and return output."""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=check)
        return result.stdout, result.stderr, result.returncode
    except subprocess.CalledProcessError as e:
        return e.stdout, e.stderr, e.returncode


def check_detect_secrets() -> None:
    """Check if detect-secrets is installed."""
    _, _, code = run_command(["detect-secrets", "--version"], check=False)
    if code != 0:
        print("ERROR: detect-secrets not found. Install with:")
        print("  pip install detect-secrets")
        sys.exit(1)


def generate_baseline() -> bool:
    """Generate or update .secrets.baseline file."""
    print("Generating secrets baseline...")

    baseline_file = Path(".secrets.baseline")

    # Exclude common non-secret patterns
    exclude_patterns = [
        "*.pyc",
        "__pycache__",
        ".git",
        ".venv",
        "venv",
        "node_modules",
        "*.egg-info",
        ".pytest_cache",
        ".ruff_cache",
        ".mypy_cache",
    ]

    cmd = ["detect-secrets", "scan", "--baseline", str(baseline_file)]
    for pattern in exclude_patterns:
        cmd.extend(["--exclude-files", pattern])
    cmd.append(".")

    _, stderr, code = run_command(cmd)

    if code == 0:
        print(f"✓ Baseline generated: {baseline_file}")
        return True
    print(f"ERROR: Failed to generate baseline\n{stderr}")
    return False


def scan_repository() -> bool:
    """Scan repository and report findings."""
    print("Scanning repository for secrets...")

    baseline_file = Path(".secrets.baseline")

    if not baseline_file.exists():
        print("WARNING: .secrets.baseline not found. Run with --baseline first.")
        return False

    cmd = ["detect-secrets", "audit", "--baseline", ".secrets.baseline"]
    stdout, stderr, code = run_command(cmd, check=False)

    if code == 0:
        print("✓ No new secrets detected")
        return True
    print("⚠ Potential secrets detected:")
    print(stdout)
    if stderr:
        print(stderr)
    return False


def main() -> None:
    parser = argparse.ArgumentParser(description="Detect secrets in the steve repository")
    parser.add_argument(
        "--baseline", action="store_true", help="Generate or update .secrets.baseline"
    )
    parser.add_argument("--scan", action="store_true", help="Scan repository and report findings")

    args = parser.parse_args()

    if not args.baseline and not args.scan:
        parser.print_help()
        sys.exit(1)

    check_detect_secrets()

    success = True

    if args.baseline:
        success = generate_baseline() and success

    if args.scan:
        success = scan_repository() and success

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
