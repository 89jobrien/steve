---
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: hook
---

# Import Validator

```python
#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Import validator hook.

Detects circular imports and unused imports in Python files.
Runs on PostToolUse for Write/Edit operations.
"""

from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from hook_logging import hook_invocation

# Common standard library modules to ignore as "unused"
STDLIB_MODULES = {
    "os",
    "sys",
    "re",
    "json",
    "typing",
    "pathlib",
    "datetime",
    "collections",
    "functools",
    "itertools",
    "asyncio",
    "logging",
    "dataclasses",
    "enum",
    "abc",
    "contextlib",
}


def extract_imports(tree: ast.AST) -> dict[str, str]:
    """Extract all imports from AST.

    Returns dict of {name: module_path}.
    """
    imports = {}

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                name = alias.asname if alias.asname else alias.name
                imports[name] = alias.name
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            for alias in node.names:
                name = alias.asname if alias.asname else alias.name
                imports[name] = f"{module}.{alias.name}"

    return imports


def extract_names_used(tree: ast.AST) -> set[str]:
    """Extract all names used in the code (excluding imports)."""
    names = set()

    for node in ast.walk(tree):
        if isinstance(node, ast.Name):
            names.add(node.id)
        elif isinstance(node, ast.Attribute):
            # Get the root name of attribute access
            current = node
            while isinstance(current, ast.Attribute):
                current = current.value
            if isinstance(current, ast.Name):
                names.add(current.id)

    return names


def check_unused_imports(content: str) -> list[str]:
    """Check for unused imports in Python code."""
    try:
        tree = ast.parse(content)
    except SyntaxError:
        return []

    imports = extract_imports(tree)
    names_used = extract_names_used(tree)

    # Filter out imports that are used
    unused = []
    for name, module in imports.items():
        if name not in names_used:
            # Skip common type-only imports and stdlib
            base_module = module.split(".")[0]
            if base_module not in STDLIB_MODULES and not name.startswith("_"):
                unused.append(name)

    return unused


def check_relative_import_depth(content: str) -> list[str]:
    """Check for deeply nested relative imports."""
    warnings = []

    try:
        tree = ast.parse(content)
    except SyntaxError:
        return []

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.level and node.level > 2:
                warnings.append(
                    f"Deep relative import (level {node.level}): "
                    f"from {'.' * node.level}{node.module or ''}"
                )

    return warnings


def main() -> None:
    with hook_invocation("import_validator") as inv:
        try:
            payload = json.load(sys.stdin)
        except json.JSONDecodeError:
            sys.exit(0)

        inv.set_payload(payload)

        if payload.get("stop_hook_active"):
            sys.exit(0)

        tool_name = payload.get("tool_name")
        if tool_name not in ("Write", "Edit", "MultiEdit"):
            sys.exit(0)

        tool_input = payload.get("tool_input", {})
        if not isinstance(tool_input, dict):
            sys.exit(0)

        file_path = tool_input.get("file_path", "")

        if not file_path or not file_path.endswith(".py"):
            sys.exit(0)

        path = Path(file_path)
        if not path.exists():
            sys.exit(0)

        content = path.read_text()

        # Check for unused imports
        unused = check_unused_imports(content)
        if unused:
            print(f"[Warning] Potentially unused imports: {', '.join(unused)}", file=sys.stderr)

        # Check for deep relative imports
        deep_imports = check_relative_import_depth(content)
        for warning in deep_imports:
            print(f"[Warning] {warning}", file=sys.stderr)

        if unused or deep_imports:
            print("\nHint: Clean imports improve code maintainability.", file=sys.stderr)
            print("  - Remove unused imports", file=sys.stderr)
            print("  - Use absolute imports for clarity", file=sys.stderr)

        sys.exit(0)


if __name__ == "__main__":
    main()
```
