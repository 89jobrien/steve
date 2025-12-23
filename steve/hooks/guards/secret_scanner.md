---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: hook
---

# Secret Scanner

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///

"""
Scan file content for exposed secrets before writing.

This hook blocks writes containing API keys, tokens, passwords, etc.
Runs before Write, Edit, or MultiEdit operations (PreToolUse).
"""

import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from hook_logging import hook_invocation

SECRET_PATTERNS = [
    # API Keys
    (r"(?i)(api[_-]?key|apikey)\s*[=:]\s*['\"]?[a-zA-Z0-9_-]{20,}['\"]?", "API key"),
    (
        r"(?i)(secret[_-]?key|secretkey)\s*[=:]\s*['\"]?[a-zA-Z0-9_-]{20,}['\"]?",
        "Secret key",
    ),
    # AWS
    (r"AKIA[0-9A-Z]{16}", "AWS Access Key ID"),
    (
        r"(?i)aws[_-]?secret[_-]?access[_-]?key\s*[=:]\s*['\"]?[a-zA-Z0-9/+=]{40}['\"]?",
        "AWS Secret Key",
    ),
    # GitHub
    (r"ghp_[a-zA-Z0-9]{36}", "GitHub Personal Access Token"),
    (r"gho_[a-zA-Z0-9]{36}", "GitHub OAuth Token"),
    (r"ghs_[a-zA-Z0-9]{36}", "GitHub Server Token"),
    (r"ghr_[a-zA-Z0-9]{36}", "GitHub Refresh Token"),
    # Generic tokens
    (
        r"(?i)(access[_-]?token|auth[_-]?token)\s*[=:]\s*['\"]?[a-zA-Z0-9_-]{20,}['\"]?",
        "Access token",
    ),
    (r"(?i)bearer\s+[a-zA-Z0-9_-]{20,}", "Bearer token"),
    # Private keys
    (r"-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----", "Private key"),
    (r"-----BEGIN PGP PRIVATE KEY BLOCK-----", "PGP private key"),
    # Passwords
    (r"(?i)(password|passwd|pwd)\s*[=:]\s*['\"]?[^\s'\"]{8,}['\"]?", "Password"),
    (
        r"(?i)(db[_-]?password|database[_-]?password)\s*[=:]\s*['\"]?[^\s'\"]+['\"]?",
        "Database password",
    ),
    # Database connection strings
    (
        r"(?i)(postgres|mysql|mongodb)://[^:]+:[^@]+@",
        "Database connection string with credentials",
    ),
    # Slack
    (r"xox[baprs]-[0-9]{10,13}-[0-9]{10,13}-[a-zA-Z0-9]{24}", "Slack token"),
    # Stripe
    (r"sk_live_[a-zA-Z0-9]{24,}", "Stripe live key"),
    (r"rk_live_[a-zA-Z0-9]{24,}", "Stripe restricted key"),
    # OpenAI/Anthropic
    (r"sk-[a-zA-Z0-9]{48}", "OpenAI API key"),
    (r"sk-ant-[a-zA-Z0-9-]{90,}", "Anthropic API key"),
    # Google
    (r"AIza[0-9A-Za-z_-]{35}", "Google API key"),
    # JWT with sensitive data
    (r"eyJ[a-zA-Z0-9_-]*\.eyJ[a-zA-Z0-9_-]*\.[a-zA-Z0-9_-]*", "JWT token"),
]

# Paths that commonly contain secrets (allowed to have them)
ALLOWED_PATHS = [
    ".env.example",
    ".env.sample",
    ".env.template",
    "example.env",
    "sample.env",
]


def get_content_to_check(tool_input: dict, tool_name: str) -> str | None:
    """Extract content to check based on tool type."""
    if tool_name == "Write":
        return tool_input.get("content")
    elif tool_name in ("Edit", "MultiEdit"):
        return tool_input.get("new_string")
    return None


def is_allowed_path(file_path: str) -> bool:
    """Check if file path is in allowed list."""
    return any(file_path.endswith(allowed) for allowed in ALLOWED_PATHS)


def scan_for_secrets(content: str) -> list[tuple[str, str]]:
    """Scan content for secrets, return list of (match, description)."""
    found = []
    for pattern, description in SECRET_PATTERNS:
        matches = re.findall(pattern, content)
        if matches:
            # Get first match for display (truncated)
            match_str = matches[0] if isinstance(matches[0], str) else str(matches[0])
            truncated = match_str[:20] + "..." if len(match_str) > 20 else match_str
            found.append((truncated, description))
    return found


def main() -> None:
    with hook_invocation("secret_scanner") as inv:
        try:
            payload = json.load(sys.stdin)
        except json.JSONDecodeError:
            sys.exit(0)

        inv.set_payload(payload)

        tool_name = payload.get("tool_name", "")
        tool_input = payload.get("tool_input", {})

        if not isinstance(tool_input, dict):
            sys.exit(0)

        file_path = tool_input.get("file_path", "")

        # Skip allowed paths
        if is_allowed_path(file_path):
            sys.exit(0)

        content = get_content_to_check(tool_input, tool_name)
        if not content:
            sys.exit(0)

        secrets_found = scan_for_secrets(content)

        if secrets_found:
            print("[Error] Potential secrets detected in content", file=sys.stderr)
            print(f"  File: {file_path}", file=sys.stderr)
            print("  Found:", file=sys.stderr)
            for match, description in secrets_found[:5]:  # Limit to 5
                print(f"    - {description}: {match}", file=sys.stderr)
            print("  Hints:", file=sys.stderr)
            print("    - Use environment variables instead", file=sys.stderr)
            print("    - Store secrets in .env (gitignored)", file=sys.stderr)
            print("    - Use a secrets manager", file=sys.stderr)
            sys.exit(2)

        sys.exit(0)


if __name__ == "__main__":
    main()
```
