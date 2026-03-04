"""Setup hooks for environment validation and workspace initialization.

Provides on-demand setup capabilities:
- Environment validation (tools, versions, env vars)
- Workspace initialization (directories, configs)
- Dependency management (check/install packages)
- Project scaffolding (detect and configure projects)

Shared utilities have been moved to lib.setup for reusability.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add hooks root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Re-export from lib.setup for backwards compatibility
from lib.setup import (  # noqa: E402
    HOOKS_ROOT,
    SetupReport,
    ValidationResult,
    check_env_var,
    get_env_var,
    load_setup_config,
)

__all__ = [
    "HOOKS_ROOT",
    "SetupReport",
    "ValidationResult",
    "check_env_var",
    "get_env_var",
    "load_setup_config",
]
