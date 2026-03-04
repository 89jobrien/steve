#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["pyyaml"]
# ///
"""Setup workflow orchestrator.

Central orchestrator for all setup tasks:
- Environment validation
- Workspace initialization
- Dependency checking
- Project scaffolding

Invoked by slash commands and returns structured JSON results.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Add hooks root to path
HOOKS_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(HOOKS_ROOT))

from hook_logging import hook_invocation  # noqa: E402, I001
from setup import SetupReport, ValidationResult  # noqa: E402, I001


def main() -> None:
    """Main entry point for setup workflow."""
    with hook_invocation("setup_workflow") as inv:
        try:
            payload = json.load(sys.stdin)
        except json.JSONDecodeError:
            payload = {}

        inv.set_payload(payload)

        # Determine which setup task to run
        task = payload.get("task", "validate")  # validate, init, deps, scaffold
        cwd = payload.get("cwd", ".")

        report = SetupReport()

        # Route to appropriate setup module
        if task == "validate":
            # Environment validation
            from setup.env_validator import validate_environment  # noqa: E402, I001

            required_tools = payload.get("required_tools", [])
            required_env_vars = payload.get("required_env_vars", [])
            report = validate_environment(required_tools, required_env_vars)

        elif task == "init":
            # Workspace initialization
            from setup.workspace_initializer import initialize_workspace  # noqa: E402, I001

            template = payload.get("template", "basic")
            auto_git_init = payload.get("auto_git_init", True)
            report = initialize_workspace(cwd, template, auto_git_init)

        elif task == "deps":
            # Dependency checking
            from setup.dependency_manager import validate_dependencies  # noqa: E402, I001

            check_outdated = payload.get("check_outdated", False)
            report = validate_dependencies(cwd, check_outdated)

        elif task == "scaffold":
            # Project scaffolding
            from setup.project_scaffolder import scaffold_project  # noqa: E402, I001

            project_type = payload.get("type")
            auto_install = payload.get("auto_install", False)
            report = scaffold_project(cwd, project_type, auto_install)

        else:
            report.add(
                ValidationResult(
                    passed=False,
                    message=f"Unknown task: {task}",
                    details={
                        "task": task,
                        "supported": ["validate", "init", "deps", "scaffold"],
                    },
                    severity="error",
                )
            )

        # Output report as JSON
        output = report.to_dict()
        print(json.dumps(output, indent=2))

        # Print summary to stderr for visibility
        if report.success:
            print(f"[Success] Setup task '{task}' completed", file=sys.stderr)
        else:
            print(
                f"[Error] Setup task '{task}' failed: {report.checks_failed} checks failed",
                file=sys.stderr,
            )

        # Exit with appropriate code
        sys.exit(0 if report.success else 1)


if __name__ == "__main__":
    main()
