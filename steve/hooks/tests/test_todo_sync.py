"""Tests for todo_sync.py hook."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch


HOOKS_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(HOOKS_ROOT / "workflows"))

from todo_sync import main, sync_todos_to_joedb  # noqa: E402


class TestSyncTodosToJoedb:
    """Tests for sync_todos_to_joedb function."""

    @patch("todo_sync.subprocess.run")
    def test_syncs_pending_todo(self, mock_run: MagicMock) -> None:
        """Should sync a pending todo to joedb."""
        mock_run.return_value = MagicMock(returncode=0)
        todos = [{"content": "Test task", "status": "pending"}]

        synced, errors = sync_todos_to_joedb(todos)

        assert synced == 1
        assert errors == 0
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert call_args[:3] == ["joedb", "todo", "add"]
        assert "Test task" in call_args
        assert "--project" in call_args
        assert "claude-session" in call_args

    @patch("todo_sync.subprocess.run")
    def test_syncs_in_progress_todo(self, mock_run: MagicMock) -> None:
        """Should sync an in_progress todo to joedb."""
        mock_run.return_value = MagicMock(returncode=0)
        todos = [{"content": "Working on it", "status": "in_progress"}]

        synced, errors = sync_todos_to_joedb(todos)

        assert synced == 1
        assert errors == 0

    @patch("todo_sync.subprocess.run")
    def test_skips_completed_todo(self, mock_run: MagicMock) -> None:
        """Should skip completed todos."""
        todos = [{"content": "Done task", "status": "completed"}]

        synced, errors = sync_todos_to_joedb(todos)

        assert synced == 0
        assert errors == 0
        mock_run.assert_not_called()

    @patch("todo_sync.subprocess.run")
    def test_skips_empty_content(self, mock_run: MagicMock) -> None:
        """Should skip todos with empty content."""
        todos = [{"content": "", "status": "pending"}]

        synced, errors = sync_todos_to_joedb(todos)

        assert synced == 0
        assert errors == 0
        mock_run.assert_not_called()

    @patch("todo_sync.subprocess.run")
    def test_handles_subprocess_error(self, mock_run: MagicMock) -> None:
        """Should count errors when subprocess fails."""
        mock_run.return_value = MagicMock(returncode=1)
        todos = [{"content": "Failing task", "status": "pending"}]

        synced, errors = sync_todos_to_joedb(todos)

        assert synced == 0
        assert errors == 1

    @patch("todo_sync.subprocess.run")
    def test_handles_timeout(self, mock_run: MagicMock) -> None:
        """Should handle subprocess timeout gracefully."""
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="joedb", timeout=5)
        todos = [{"content": "Timeout task", "status": "pending"}]

        synced, errors = sync_todos_to_joedb(todos)

        assert synced == 0
        assert errors == 1

    @patch("todo_sync.subprocess.run")
    def test_handles_missing_joedb(self, mock_run: MagicMock) -> None:
        """Should handle missing joedb command gracefully."""
        mock_run.side_effect = FileNotFoundError()
        todos = [{"content": "Missing cmd", "status": "pending"}]

        synced, errors = sync_todos_to_joedb(todos)

        assert synced == 0
        assert errors == 1

    @patch("todo_sync.subprocess.run")
    def test_multiple_todos_mixed_status(self, mock_run: MagicMock) -> None:
        """Should process multiple todos with mixed statuses."""
        mock_run.return_value = MagicMock(returncode=0)
        todos = [
            {"content": "Pending one", "status": "pending"},
            {"content": "Done one", "status": "completed"},
            {"content": "In progress", "status": "in_progress"},
            {"content": "Another done", "status": "completed"},
        ]

        synced, errors = sync_todos_to_joedb(todos)

        assert synced == 2  # Only pending and in_progress
        assert errors == 0
        assert mock_run.call_count == 2

    @patch("todo_sync.subprocess.run")
    def test_tags_include_status(self, mock_run: MagicMock) -> None:
        """Should include status in tags."""
        mock_run.return_value = MagicMock(returncode=0)
        todos = [{"content": "Tagged task", "status": "in_progress"}]

        sync_todos_to_joedb(todos)

        call_args = mock_run.call_args[0][0]
        tags_idx = call_args.index("--tags") + 1
        assert call_args[tags_idx] == "claude,in_progress"


class TestMain:
    """Tests for main entry point."""

    @patch.dict("os.environ", {"CLAUDE_TOOL_INPUT": "{}"})
    @patch("todo_sync.sync_todos_to_joedb")
    def test_empty_input_returns_early(self, mock_sync: MagicMock) -> None:
        """Should return 0 for empty input without syncing."""
        result = main()

        assert result == 0
        mock_sync.assert_not_called()

    @patch.dict("os.environ", {"CLAUDE_TOOL_INPUT": '{"todos": []}'})
    @patch("todo_sync.sync_todos_to_joedb")
    def test_empty_todos_returns_early(self, mock_sync: MagicMock) -> None:
        """Should return 0 for empty todos list."""
        result = main()

        assert result == 0
        mock_sync.assert_not_called()

    @patch.dict(
        "os.environ",
        {"CLAUDE_TOOL_INPUT": '{"todos": [{"content": "Done", "status": "completed"}]}'},
    )
    @patch("todo_sync.sync_todos_to_joedb")
    def test_only_completed_todos_returns_early(self, mock_sync: MagicMock) -> None:
        """Should return 0 when all todos are completed."""
        result = main()

        assert result == 0
        mock_sync.assert_not_called()

    @patch.dict("os.environ", {"CLAUDE_TOOL_INPUT": "invalid json"})
    @patch("todo_sync.sync_todos_to_joedb")
    def test_invalid_json_returns_early(self, mock_sync: MagicMock) -> None:
        """Should handle invalid JSON gracefully."""
        result = main()

        assert result == 0
        mock_sync.assert_not_called()

    @patch.dict(
        "os.environ",
        {
            "CLAUDE_TOOL_INPUT": json.dumps(
                {"todos": [{"content": "Active task", "status": "pending"}]}
            )
        },
    )
    @patch("todo_sync.sync_todos_to_joedb")
    def test_syncs_active_todos(self, mock_sync: MagicMock) -> None:
        """Should sync active todos."""
        mock_sync.return_value = (1, 0)

        result = main()

        assert result == 0
        mock_sync.assert_called_once()
        call_args = mock_sync.call_args[0][0]
        assert len(call_args) == 1
        assert call_args[0]["content"] == "Active task"
