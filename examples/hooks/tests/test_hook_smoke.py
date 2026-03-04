import subprocess
import sys
import unittest
from pathlib import Path

HOOKS_ROOT = Path(__file__).resolve().parents[1]
if str(HOOKS_ROOT) not in sys.path:
    sys.path.insert(0, str(HOOKS_ROOT))

import claude_hooks  # noqa: E402


class TestHookSmoke(unittest.TestCase):
    def test_list_hook_scripts_includes_guard(self) -> None:
        scripts = claude_hooks.list_hook_scripts()
        self.assertTrue(
            any(script.name == "dangerous_command_guard.py" for script in scripts),
            "Expected dangerous_command_guard.py to be listed",
        )

    def test_hook_scripts_run_quickly(self) -> None:
        scripts = claude_hooks.list_hook_scripts()
        for script in scripts:
            result = subprocess.run(
                ["uv", "run", str(script)],
                input="",
                text=True,
                capture_output=True,
                timeout=10,
            )
            if result.returncode != 0:
                self.fail(
                    f"Hook script failed: {script}\n"
                    f"stdout: {result.stdout}\n"
                    f"stderr: {result.stderr}"
                )


if __name__ == "__main__":
    unittest.main()
