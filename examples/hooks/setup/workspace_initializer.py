#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml"]
# ///
"""Workspace initializer for setup hooks.

Creates standard directory structures and configuration files:
- Project directories (src/, tests/, docs/)
- Configuration files (pyproject.toml, .gitignore, etc.)
- Git repository initialization
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from hook_logging import hook_invocation  # noqa: E402, I001
from lib.setup import SetupReport, ValidationResult, load_setup_config  # noqa: E402, I001


# Template definitions
TEMPLATES = {
    "basic": {
        "dirs": [".claude", "docs"],
        "files": {
            ".gitignore": "*.pyc\n__pycache__/\n.DS_Store\n*.log\n",
            "README.md": "# Project\n\nDescription of your project.\n",
        },
    },
    "python": {
        "dirs": ["src", "tests", "docs", ".claude"],
        "files": {
            "pyproject.toml": """[project]
name = "my-project"
version = "0.1.0"
description = "Python project"
requires-python = ">=3.12"
dependencies = []

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.ruff]
line-length = 120
target-version = "py312"
""",
            ".gitignore": """# Python
*.pyc
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
Thumbs.db

# Logs
*.log
""",
            "README.md": "# Python Project\n\nDescription of your Python project.\n\n## Setup\n\n```bash\nuv sync\n```\n",
        },
    },
    "node": {
        "dirs": ["src", "test", "docs", ".claude"],
        "files": {
            "package.json": """{
  "name": "my-project",
  "version": "0.1.0",
  "description": "Node.js project",
  "main": "src/index.js",
  "scripts": {
    "test": "echo \\"Error: no test specified\\" && exit 1"
  },
  "keywords": [],
  "author": "",
  "license": "MIT"
}
""",
            ".gitignore": """# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
.pnpm-debug.log*

# Build output
dist/
build/
*.tsbuildinfo

# Environment
.env
.env.local
.env.*.local

# IDEs
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Logs
logs/
*.log
""",
            "README.md": "# Node.js Project\n\nDescription of your Node.js project.\n\n## Setup\n\n```bash\nnpm install\n```\n",
        },
    },
    "full-stack": {
        "dirs": [
            "frontend/src",
            "frontend/public",
            "backend/src",
            "backend/tests",
            "docs",
            ".claude",
        ],
        "files": {
            ".gitignore": """# Dependencies
node_modules/
.venv/
__pycache__/

# Build output
dist/
build/
*.egg-info/

# Environment
.env
.env.local

# IDEs
.vscode/
.idea/

# OS
.DS_Store

# Logs
*.log
""",
            "README.md": "# Full-Stack Project\n\n## Structure\n\n- `frontend/` - Frontend application\n- `backend/` - Backend API\n- `docs/` - Documentation\n",
        },
    },
}


def create_directory(path: Path) -> ValidationResult:
    """Create a directory if it doesn't exist.

    Args:
        path: Directory path to create

    Returns:
        ValidationResult
    """
    try:
        if path.exists():
            if path.is_dir():
                return ValidationResult(
                    passed=True,
                    message=f"Directory {path} already exists",
                    details={"path": str(path), "created": False},
                    severity="info",
                )
            return ValidationResult(
                passed=False,
                message=f"Path {path} exists but is not a directory",
                details={"path": str(path)},
                severity="error",
            )

        path.mkdir(parents=True, exist_ok=True)
        return ValidationResult(
            passed=True,
            message=f"Created directory {path}",
            details={"path": str(path), "created": True},
        )
    except OSError as e:
        return ValidationResult(
            passed=False,
            message=f"Failed to create directory {path}: {e}",
            details={"path": str(path), "error": str(e)},
            severity="error",
        )


def create_file(path: Path, content: str, overwrite: bool = False) -> ValidationResult:
    """Create a file with content.

    Args:
        path: File path to create
        content: File content
        overwrite: Whether to overwrite existing file

    Returns:
        ValidationResult
    """
    try:
        if path.exists() and not overwrite:
            return ValidationResult(
                passed=True,
                message=f"File {path.name} already exists (skipped)",
                details={"path": str(path), "created": False, "skipped": True},
                severity="info",
            )

        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)

        return ValidationResult(
            passed=True,
            message=f"Created file {path.name}",
            details={"path": str(path), "created": True},
        )
    except OSError as e:
        return ValidationResult(
            passed=False,
            message=f"Failed to create file {path}: {e}",
            details={"path": str(path), "error": str(e)},
            severity="error",
        )


def initialize_workspace(
    cwd: str | Path,
    template: str = "basic",
    auto_git_init: bool = True,
) -> SetupReport:
    """Initialize workspace with template.

    Args:
        cwd: Working directory
        template: Template name (basic, python, node, full-stack)
        auto_git_init: Whether to initialize git repository

    Returns:
        SetupReport
    """
    report = SetupReport()
    cwd_path = Path(cwd)

    # Get template
    template_config = TEMPLATES.get(template)
    if not template_config:
        report.add(
            ValidationResult(
                passed=False,
                message=f"Unknown template: {template}",
                details={"template": template, "available": list(TEMPLATES.keys())},
                severity="error",
            )
        )
        return report

    # Create directories
    for dir_path in template_config.get("dirs", []):
        full_path = cwd_path / dir_path
        result = create_directory(full_path)
        report.add(result)

    # Create files
    for file_path, content in template_config.get("files", {}).items():
        full_path = cwd_path / file_path
        result = create_file(full_path, content, overwrite=False)
        report.add(result)

    # Initialize git repository if requested
    if auto_git_init and not (cwd_path / ".git").exists():
        import subprocess

        try:
            result = subprocess.run(
                ["git", "init"],
                cwd=cwd_path,
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode == 0:
                report.add(
                    ValidationResult(
                        passed=True,
                        message="Initialized git repository",
                        details={"git_init": True},
                    )
                )
            else:
                report.add(
                    ValidationResult(
                        passed=False,
                        message="Failed to initialize git repository",
                        details={"error": result.stderr},
                        severity="warning",
                    )
                )
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError) as e:
            report.add(
                ValidationResult(
                    passed=False,
                    message=f"Git initialization failed: {e}",
                    details={"error": str(e)},
                    severity="warning",
                )
            )

    return report


def main() -> None:
    """Main entry point for workspace initialization."""
    with hook_invocation("workspace_initializer") as inv:
        try:
            payload = json.load(sys.stdin)
        except json.JSONDecodeError:
            payload = {}

        inv.set_payload(payload)

        # Load configuration
        config = load_setup_config()
        workspace_config = config.get("workspace_init", {})

        # Get parameters
        cwd = payload.get("cwd", ".")
        template = payload.get("template") or workspace_config.get("default_template", "basic")
        auto_git_init = payload.get("auto_git_init", workspace_config.get("auto_git_init", True))

        # Run initialization
        report = initialize_workspace(cwd, template, auto_git_init)

        # Output report as JSON
        output = report.to_dict()
        print(json.dumps(output, indent=2))

        # Exit with appropriate code
        sys.exit(0 if report.success else 1)


if __name__ == "__main__":
    main()
