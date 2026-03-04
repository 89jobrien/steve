#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml"]
# ///
"""Project scaffolder for setup hooks.

Detects and scaffolds new projects:
- Detects project type (Next.js, FastAPI, Django, etc.)
- Runs framework initialization commands
- Creates boilerplate files
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from hook_logging import hook_invocation  # noqa: E402, I001
from lib.detection import detect_project_type  # noqa: E402, I001
from lib.setup import SetupReport, ValidationResult, load_setup_config  # noqa: E402, I001
from lib.subprocess import command_exists  # noqa: E402, I001


# Framework initialization commands
SCAFFOLD_COMMANDS = {
    "nextjs": {
        "check": "npx",
        "command": ["npx", "create-next-app@latest", ".", "--use-npm"],
        "description": "Next.js application with App Router",
    },
    "fastapi": {
        "check": "uv",
        "command": ["uv", "init", "--lib"],
        "description": "FastAPI Python project",
        "files": {
            "main.py": '''"""FastAPI application entry point."""
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    """Root endpoint."""
    return {"message": "Hello World"}


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
''',
        },
    },
    "django": {
        "check": "django-admin",
        "command": ["django-admin", "startproject", "myproject", "."],
        "description": "Django web application",
    },
    "flask": {
        "check": "uv",
        "command": ["uv", "init"],
        "description": "Flask web application",
        "files": {
            "app.py": '''"""Flask application entry point."""
from flask import Flask, jsonify

app = Flask(__name__)


@app.route("/")
def hello():
    """Root endpoint."""
    return jsonify({"message": "Hello World"})


@app.route("/health")
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy"})


if __name__ == "__main__":
    app.run(debug=True)
''',
        },
    },
    "rust": {
        "check": "cargo",
        "command": ["cargo", "init"],
        "description": "Rust project with Cargo",
    },
    "go": {
        "check": "go",
        "command": ["go", "mod", "init", "example.com/myproject"],
        "description": "Go module",
    },
    "python": {
        "check": "uv",
        "command": ["uv", "init"],
        "description": "Python project with uv",
    },
}


def scaffold_project(
    cwd: str | Path,
    project_type: str | None = None,
    auto_install: bool = False,
) -> SetupReport:
    """Scaffold a new project.

    Args:
        cwd: Project directory
        project_type: Project type to scaffold (auto-detect if None)
        auto_install: Whether to automatically install dependencies

    Returns:
        SetupReport
    """
    report = SetupReport()
    cwd_path = Path(cwd)

    # Auto-detect project type if not specified
    if not project_type:
        detected = detect_project_type(cwd_path)
        if detected.project_type:
            project_type = detected.project_type
            report.add(
                ValidationResult(
                    passed=True,
                    message=f"Detected existing project type: {project_type}",
                    details={"project_type": project_type, "auto_detected": True},
                )
            )
        else:
            report.add(
                ValidationResult(
                    passed=False,
                    message="Could not detect project type. Please specify --type=<framework>",
                    details={"supported": list(SCAFFOLD_COMMANDS.keys())},
                    severity="error",
                )
            )
            return report

    # Get scaffold configuration
    scaffold_config = SCAFFOLD_COMMANDS.get(project_type)
    if not scaffold_config:
        report.add(
            ValidationResult(
                passed=False,
                message=f"Unknown project type: {project_type}",
                details={
                    "project_type": project_type,
                    "supported": list(SCAFFOLD_COMMANDS.keys()),
                },
                severity="error",
            )
        )
        return report

    # Check if required tool exists
    required_tool = scaffold_config["check"]
    if not command_exists(required_tool):
        report.add(
            ValidationResult(
                passed=False,
                message=f"Required tool '{required_tool}' not found",
                details={"tool": required_tool, "project_type": project_type},
                severity="error",
            )
        )
        return report

    # Check if directory is empty (or mostly empty)
    existing_files = list(cwd_path.iterdir())
    non_hidden = [f for f in existing_files if not f.name.startswith(".")]
    if len(non_hidden) > 0:
        report.add(
            ValidationResult(
                passed=False,
                message=f"Directory not empty ({len(non_hidden)} files/dirs found)",
                details={"file_count": len(non_hidden)},
                severity="warning",
            )
        )
        # Continue anyway for now

    # Run scaffold command
    command = scaffold_config["command"]
    description = scaffold_config["description"]

    try:
        result = subprocess.run(
            command,
            cwd=cwd_path,
            capture_output=True,
            text=True,
            timeout=120,  # Allow 2 minutes for initialization
        )

        if result.returncode == 0:
            report.add(
                ValidationResult(
                    passed=True,
                    message=f"Scaffolded {description}",
                    details={
                        "project_type": project_type,
                        "command": " ".join(command),
                    },
                )
            )
        else:
            report.add(
                ValidationResult(
                    passed=False,
                    message=f"Scaffold command failed: {result.stderr}",
                    details={"command": " ".join(command), "error": result.stderr},
                    severity="error",
                )
            )
            return report

    except subprocess.TimeoutExpired:
        report.add(
            ValidationResult(
                passed=False,
                message="Scaffold command timed out",
                details={"command": " ".join(command)},
                severity="error",
            )
        )
        return report
    except (FileNotFoundError, OSError) as e:
        report.add(
            ValidationResult(
                passed=False,
                message=f"Failed to run scaffold command: {e}",
                details={"command": " ".join(command), "error": str(e)},
                severity="error",
            )
        )
        return report

    # Create additional files if specified
    files = scaffold_config.get("files", {})
    for file_path, content in files.items():
        full_path = cwd_path / file_path
        try:
            full_path.write_text(content)
            report.add(
                ValidationResult(
                    passed=True,
                    message=f"Created {file_path}",
                    details={"file": file_path},
                )
            )
        except OSError as e:
            report.add(
                ValidationResult(
                    passed=False,
                    message=f"Failed to create {file_path}: {e}",
                    details={"file": file_path, "error": str(e)},
                    severity="warning",
                )
            )

    return report


def main() -> None:
    """Main entry point for project scaffolding."""
    with hook_invocation("project_scaffolder") as inv:
        try:
            payload = json.load(sys.stdin)
        except json.JSONDecodeError:
            payload = {}

        inv.set_payload(payload)

        # Load configuration
        config = load_setup_config()
        scaffold_config = config.get("project_scaffold", {})

        # Get parameters
        cwd = payload.get("cwd", ".")
        project_type = payload.get("type")
        auto_install = payload.get("auto_install", scaffold_config.get("auto_install_deps", False))

        # Run scaffolding
        report = scaffold_project(cwd, project_type, auto_install)

        # Output report as JSON
        output = report.to_dict()
        print(json.dumps(output, indent=2))

        # Exit with appropriate code
        sys.exit(0 if report.success else 1)


if __name__ == "__main__":
    main()
