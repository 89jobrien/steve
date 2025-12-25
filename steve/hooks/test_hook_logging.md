---
name: test-hook-logging
description: Test Hook Logging hook implementation
author: Joseph OBrien
status: unpublished
updated: 2025-12-23
version: 1.0.1
tag: hook
---
# Test Hook Logging

```python
import io
import json
import os
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch


class TestHookLogging(unittest.TestCase):
    def test_logs_to_daily_jsonl_and_breadcrumb(self) -> None:
        hooks_dir = Path(__file__).resolve().parent
        sys.path.insert(0, str(hooks_dir))
        try:
            import hook_logging

            with tempfile.TemporaryDirectory() as td:
                log_dir = Path(td)
                fixed_start = datetime(2025, 12, 17, 1, 2, 3)
                fixed_end = datetime(2025, 12, 17, 1, 2, 4)

                stderr = io.StringIO()
                payload = {
                    "cwd": "/repo",
                    "tool_name": "Write",
                    "tool_input": {"file_path": "/repo/a.py"},
                }

                with patch.dict(
                    os.environ, {"CLAUDE_HOOK_LOG_DIR": str(log_dir)}, clear=False
                ):
                    with patch.object(hook_logging, "datetime") as dt:
                        dt.now.side_effect = [fixed_start, fixed_end]
                        with patch.object(
                            hook_logging.time, "monotonic", side_effect=[10.0, 10.123]
                        ):
                            with patch.object(sys, "stderr", stderr):
                                with hook_logging.hook_invocation(
                                    "secret_scanner"
                                ) as inv:
                                    inv.set_payload(payload)

                log_path = log_dir / "hooks_20251217.jsonl"
                self.assertTrue(log_path.exists())
                rec = json.loads(log_path.read_text().strip())

                self.assertEqual(rec["hook_name"], "secret_scanner")
                self.assertEqual(rec["exit_code"], 0)
                self.assertTrue(rec["ok"])
                self.assertEqual(rec["start_ts"], fixed_start.isoformat())
                self.assertEqual(rec["end_ts"], fixed_end.isoformat())
                self.assertEqual(rec["cwd"], "/repo")
                self.assertEqual(rec["tool_name"], "Write")
                self.assertEqual(rec["tool_input.file_path"], "/repo/a.py")
                self.assertEqual(rec["duration_ms"], 123)

                self.assertIn("[HookLog]", stderr.getvalue())
                self.assertIn("hook=secret_scanner", stderr.getvalue())
                self.assertIn("exit=0", stderr.getvalue())
        finally:
            sys.path.remove(str(hooks_dir))

    def test_logs_systemexit_nonzero(self) -> None:
        hooks_dir = Path(__file__).resolve().parent
        sys.path.insert(0, str(hooks_dir))
        try:
            import hook_logging

            with tempfile.TemporaryDirectory() as td:
                log_dir = Path(td)
                fixed_start = datetime(2025, 12, 17, 1, 2, 3)
                fixed_end = datetime(2025, 12, 17, 1, 2, 4)

                with patch.dict(
                    os.environ, {"CLAUDE_HOOK_LOG_DIR": str(log_dir)}, clear=False
                ):
                    with patch.object(hook_logging, "datetime") as dt:
                        dt.now.side_effect = [fixed_start, fixed_end]
                        with patch.object(
                            hook_logging.time, "monotonic", side_effect=[10.0, 10.010]
                        ):
                            stderr = io.StringIO()
                            with patch.object(sys, "stderr", stderr):
                                with self.assertRaises(SystemExit) as cm:
                                    with hook_logging.hook_invocation(
                                        "dangerous_command_guard"
                                    ):
                                        raise SystemExit(2)

                self.assertEqual(cm.exception.code, 2)

                log_path = log_dir / "hooks_20251217.jsonl"
                rec = json.loads(log_path.read_text().strip())
                self.assertEqual(rec["hook_name"], "dangerous_command_guard")
                self.assertEqual(rec["exit_code"], 2)
                self.assertFalse(rec["ok"])
        finally:
            sys.path.remove(str(hooks_dir))


if __name__ == "__main__":
    unittest.main()
```
