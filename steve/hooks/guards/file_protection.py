#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///

"""Prevent modifications to critical files.

This hook blocks writes to sensitive files like .env, credentials, production configs.
Runs before Write, Edit, or MultiEdit operations (PreToolUse).
"""

import json
import re
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent.parent))
from hook_logging import hook_invocation


# Exact file names to protect
PROTECTED_FILES = [
    ".env",
    ".env.local",
    ".env.production",
    ".env.prod",
    "credentials.json",
    "service-account.json",
    "secrets.json",
    "secrets.yaml",
    "secrets.yml",
    ".npmrc",
    ".pypirc",
    ".netrc",
    ".docker/config.json",
    "id_rsa",
    "id_ed25519",
    "id_ecdsa",
    ".ssh/config",
]

# Patterns for protected files
PROTECTED_PATTERNS = [
    r".*\.pem$",
    r".*\.key$",
    r".*\.p12$",
    r".*\.pfx$",
    r".*_rsa$",
    r".*_ed25519$",
    r".*_ecdsa$",
    r".*credentials.*\.json$",
    r".*secrets.*\.(json|yaml|yml)$",
    r".*service[-_]?account.*\.json$",
    r"\.env\.[a-z]+$",  # .env.* files
]

# Paths that contain production configs
PROTECTED_PATH_PARTS = [
    "/prod/",
    "/production/",
    "/live/",
    "/.aws/",
    "/.ssh/",
    "/.gnupg/",
    "/.kube/",
]


def is_protected_file(file_path: str) -> tuple[bool, str | None]:
    """Check if file path matches protected patterns."""
    path = Path(file_path)
    filename = path.name

    # Check exact matches
    for protected in PROTECTED_FILES:
        if filename == protected or file_path.endswith(f"/{protected}"):
            return True, f"Protected file: {protected}"

    # Check patterns
    for pattern in PROTECTED_PATTERNS:
        if re.match(pattern, filename, re.IGNORECASE):
            return True, f"Matches protected pattern: {pattern}"

    # Check path parts
    for part in PROTECTED_PATH_PARTS:
        if part in file_path:
            return True, f"Protected path contains: {part}"

    return False, None


def main() -> None:
    with hook_invocation("file_protection") as inv:
        try:
            payload = json.load(sys.stdin)
        except json.JSONDecodeError:
            sys.exit(0)

        inv.set_payload(payload)

        tool_input = payload.get("tool_input", {})

        if not isinstance(tool_input, dict):
            sys.exit(0)

        file_path = tool_input.get("file_path", "")

        if not file_path:
            sys.exit(0)

        is_protected, reason = is_protected_file(file_path)

        if is_protected:
            print("[Error] Cannot modify protected file", file=sys.stderr)
            print(f"  File: {file_path}", file=sys.stderr)
            print(f"  Reason: {reason}", file=sys.stderr)
            print("  Hints:", file=sys.stderr)
            print("    - Edit this file manually if changes are needed", file=sys.stderr)
            print("    - Use environment variables for configuration", file=sys.stderr)
            print("    - Consider using a secrets manager", file=sys.stderr)
            sys.exit(2)

        sys.exit(0)


if __name__ == "__main__":
    main()
