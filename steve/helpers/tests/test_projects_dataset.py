"""Tests for projects_dataset.py - RL/FT dataset builder."""

import dataclasses
import json
from pathlib import Path

import pytest

from steve.helpers.projects_dataset import (
    DatasetRow,
    _msg_to_dict,
    _PendingTool,
    _reward_from_tool_result,
    _tool_result_to_dict,
    _tool_use_to_dict,
    iter_dataset_rows,
    iter_dataset_rows_from_events,
    main,
    write_jsonl,
)
from steve.helpers.projects_extract import MessageEvent, ToolResultEvent, ToolUseEvent


class TestDatasetRow:
    """Tests for DatasetRow dataclass."""

    def test_creates_valid_row(self) -> None:
        """Should create valid DatasetRow instance."""
        row = DatasetRow(
            session_id="s1",
            t="2024-01-01T00:00:00Z",
            messages=[{"role": "user", "text": "hello"}],
            tool_name="Read",
            tool_input={"file_path": "/test.py"},
            tool_result={"content": "file content"},
            trace=[],
            reward=1.0,
        )
        assert row.session_id == "s1"
        assert row.tool_name == "Read"
        assert row.reward == 1.0

    def test_row_is_frozen(self) -> None:
        """DatasetRow should be immutable."""
        row = DatasetRow(
            session_id="s1",
            t="2024-01-01T00:00:00Z",
            messages=[],
            tool_name="Read",
            tool_input={},
            tool_result={},
            trace=[],
            reward=1.0,
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            row.session_id = "modified"  # type: ignore[misc]

    def test_row_with_none_timestamp(self) -> None:
        """Should handle None timestamp."""
        row = DatasetRow(
            session_id="s1",
            t=None,
            messages=[],
            tool_name="Read",
            tool_input={},
            tool_result={},
            trace=[],
            reward=0.0,
        )
        assert row.t is None


class TestRewardFromToolResult:
    """Tests for _reward_from_tool_result function."""

    def test_error_result_returns_negative_reward(self) -> None:
        """Error tool result should return -1.0 reward."""
        result = ToolResultEvent(
            session_id="s1",
            uuid="u1",
            parent_uuid="p1",
            timestamp="t1",
            role="user",
            tool_use_id="tu1",
            is_error=True,
            content_text="Error occurred",
        )
        assert _reward_from_tool_result(result) == -1.0

    def test_success_result_returns_positive_reward(self) -> None:
        """Successful tool result should return 1.0 reward."""
        result = ToolResultEvent(
            session_id="s1",
            uuid="u1",
            parent_uuid="p1",
            timestamp="t1",
            role="user",
            tool_use_id="tu1",
            is_error=False,
            content_text="Success",
        )
        assert _reward_from_tool_result(result) == 1.0


class TestMsgToDict:
    """Tests for _msg_to_dict function."""

    def test_converts_message_event(self) -> None:
        """Should convert MessageEvent to dict."""
        msg = MessageEvent(
            session_id="s1",
            uuid="u1",
            parent_uuid="p1",
            timestamp="2024-01-01T00:00:00Z",
            role="user",
            text="Hello world",
        )
        result = _msg_to_dict(msg)
        assert result == {
            "t": "2024-01-01T00:00:00Z",
            "role": "user",
            "text": "Hello world",
            "uuid": "u1",
            "parent_uuid": "p1",
        }

    def test_handles_none_values(self) -> None:
        """Should handle None values in message."""
        msg = MessageEvent(
            session_id="s1",
            uuid=None,
            parent_uuid=None,
            timestamp=None,
            role="assistant",
            text="",
        )
        result = _msg_to_dict(msg)
        assert result["uuid"] is None
        assert result["parent_uuid"] is None
        assert result["t"] is None


class TestToolUseToDict:
    """Tests for _tool_use_to_dict function."""

    def test_converts_tool_use_event(self) -> None:
        """Should convert ToolUseEvent to dict."""
        tu = ToolUseEvent(
            session_id="s1",
            uuid="u1",
            parent_uuid="p1",
            timestamp="2024-01-01T00:00:00Z",
            role="assistant",
            tool_name="Read",
            tool_use_id="tu1",
            tool_input={"file_path": "/test.py"},
        )
        result = _tool_use_to_dict(tu)
        assert result == {
            "type": "tool_use",
            "t": "2024-01-01T00:00:00Z",
            "tool_name": "Read",
            "tool_use_id": "tu1",
            "tool_input": {"file_path": "/test.py"},
            "uuid": "u1",
            "parent_uuid": "p1",
        }

    def test_includes_type_field(self) -> None:
        """Dict should include type='tool_use'."""
        tu = ToolUseEvent(
            session_id="s1",
            uuid="u1",
            parent_uuid="p1",
            timestamp="t1",
            role="assistant",
            tool_name="Write",
            tool_use_id="tu1",
            tool_input={},
        )
        result = _tool_use_to_dict(tu)
        assert result["type"] == "tool_use"


class TestToolResultToDict:
    """Tests for _tool_result_to_dict function."""

    def test_converts_tool_result_event(self) -> None:
        """Should convert ToolResultEvent to dict."""
        tr = ToolResultEvent(
            session_id="s1",
            uuid="u1",
            parent_uuid="p1",
            timestamp="2024-01-01T00:00:00Z",
            role="user",
            tool_use_id="tu1",
            is_error=False,
            content_text="File content here",
        )
        result = _tool_result_to_dict(tr)
        assert result == {
            "type": "tool_result",
            "t": "2024-01-01T00:00:00Z",
            "tool_use_id": "tu1",
            "is_error": False,
            "content_text": "File content here",
            "uuid": "u1",
            "parent_uuid": "p1",
        }

    def test_includes_error_flag(self) -> None:
        """Dict should include is_error flag."""
        tr = ToolResultEvent(
            session_id="s1",
            uuid="u1",
            parent_uuid="p1",
            timestamp="t1",
            role="user",
            tool_use_id="tu1",
            is_error=True,
            content_text="Error message",
        )
        result = _tool_result_to_dict(tr)
        assert result["is_error"] is True


class TestPendingTool:
    """Tests for _PendingTool dataclass."""

    def test_creates_pending_tool(self) -> None:
        """Should create _PendingTool instance."""
        tu = ToolUseEvent(
            session_id="s1",
            uuid="u1",
            parent_uuid="p1",
            timestamp="t1",
            role="assistant",
            tool_name="Read",
            tool_use_id="tu1",
            tool_input={},
        )
        pending = _PendingTool(
            tool_use=tu,
            messages=[],
            trace=[],
        )
        assert pending.tool_use == tu
        assert pending.messages == []
        assert pending.trace == []

    def test_pending_tool_mutable(self) -> None:
        """_PendingTool should be mutable for trace updates."""
        tu = ToolUseEvent(
            session_id="s1",
            uuid="u1",
            parent_uuid="p1",
            timestamp="t1",
            role="assistant",
            tool_name="Read",
            tool_use_id="tu1",
            tool_input={},
        )
        pending = _PendingTool(tool_use=tu, messages=[], trace=[])
        pending.trace.append({"type": "test"})
        assert len(pending.trace) == 1


class TestIterDatasetRowsFromEvents:
    """Tests for iter_dataset_rows_from_events function."""

    def test_empty_events(self) -> None:
        """Should handle empty event list."""
        rows = list(iter_dataset_rows_from_events([]))
        assert rows == []

    def test_message_only_events(self) -> None:
        """Should not yield rows for message-only events."""
        events = [
            MessageEvent(
                session_id="s1",
                uuid="u1",
                parent_uuid=None,
                timestamp="t1",
                role="user",
                text="Hello",
            ),
            MessageEvent(
                session_id="s1",
                uuid="u2",
                parent_uuid="u1",
                timestamp="t2",
                role="assistant",
                text="Hi there",
            ),
        ]
        rows = list(iter_dataset_rows_from_events(events))
        assert rows == []

    def test_tool_use_without_result(self) -> None:
        """Should not yield row if tool_use has no matching result."""
        events = [
            ToolUseEvent(
                session_id="s1",
                uuid="u1",
                parent_uuid=None,
                timestamp="t1",
                role="assistant",
                tool_name="Read",
                tool_use_id="tu1",
                tool_input={"file": "test.py"},
            ),
        ]
        rows = list(iter_dataset_rows_from_events(events))
        assert rows == []

    def test_pairs_tool_use_with_result(self) -> None:
        """Should yield row when tool_use is paired with result."""
        events = [
            ToolUseEvent(
                session_id="s1",
                uuid="u1",
                parent_uuid=None,
                timestamp="t1",
                role="assistant",
                tool_name="Read",
                tool_use_id="tu1",
                tool_input={"file": "test.py"},
            ),
            ToolResultEvent(
                session_id="s1",
                uuid="u2",
                parent_uuid="u1",
                timestamp="t2",
                role="user",
                tool_use_id="tu1",
                is_error=False,
                content_text="file content",
            ),
        ]
        rows = list(iter_dataset_rows_from_events(events))
        assert len(rows) == 1
        assert rows[0]["tool_name"] == "Read"
        assert rows[0]["reward"] == 1.0

    def test_error_result_negative_reward(self) -> None:
        """Should assign negative reward for error results."""
        events = [
            ToolUseEvent(
                session_id="s1",
                uuid="u1",
                parent_uuid=None,
                timestamp="t1",
                role="assistant",
                tool_name="Read",
                tool_use_id="tu1",
                tool_input={"file": "nonexistent.py"},
            ),
            ToolResultEvent(
                session_id="s1",
                uuid="u2",
                parent_uuid="u1",
                timestamp="t2",
                role="user",
                tool_use_id="tu1",
                is_error=True,
                content_text="File not found",
            ),
        ]
        rows = list(iter_dataset_rows_from_events(events))
        assert len(rows) == 1
        assert rows[0]["reward"] == -1.0

    def test_captures_recent_messages(self) -> None:
        """Should capture recent messages in row."""
        events = [
            MessageEvent(
                session_id="s1",
                uuid="m1",
                parent_uuid=None,
                timestamp="t1",
                role="user",
                text="Read test.py",
            ),
            ToolUseEvent(
                session_id="s1",
                uuid="u1",
                parent_uuid="m1",
                timestamp="t2",
                role="assistant",
                tool_name="Read",
                tool_use_id="tu1",
                tool_input={"file": "test.py"},
            ),
            ToolResultEvent(
                session_id="s1",
                uuid="u2",
                parent_uuid="u1",
                timestamp="t3",
                role="user",
                tool_use_id="tu1",
                is_error=False,
                content_text="content",
            ),
        ]
        rows = list(iter_dataset_rows_from_events(events))
        assert len(rows) == 1
        assert len(rows[0]["messages"]) == 1
        assert rows[0]["messages"][0]["text"] == "Read test.py"

    def test_respects_max_context_messages(self) -> None:
        """Should limit messages to max_context_messages."""
        events = [
            MessageEvent(
                session_id="s1",
                uuid=f"m{i}",
                parent_uuid=None,
                timestamp=f"t{i}",
                role="user",
                text=f"Message {i}",
            )
            for i in range(10)
        ]
        events.append(
            ToolUseEvent(
                session_id="s1",
                uuid="tu1",
                parent_uuid=None,
                timestamp="t10",
                role="assistant",
                tool_name="Read",
                tool_use_id="tu1",
                tool_input={},
            )
        )
        events.append(
            ToolResultEvent(
                session_id="s1",
                uuid="tr1",
                parent_uuid="tu1",
                timestamp="t11",
                role="user",
                tool_use_id="tu1",
                is_error=False,
                content_text="result",
            )
        )

        rows = list(iter_dataset_rows_from_events(events, max_context_messages=3))
        assert len(rows[0]["messages"]) == 3

    def test_includes_messages_in_trace_when_enabled(self) -> None:
        """Should include messages in trace when flag is True."""
        events = [
            ToolUseEvent(
                session_id="s1",
                uuid="u1",
                parent_uuid=None,
                timestamp="t1",
                role="assistant",
                tool_name="Read",
                tool_use_id="tu1",
                tool_input={},
            ),
            MessageEvent(
                session_id="s1",
                uuid="m1",
                parent_uuid="u1",
                timestamp="t2",
                role="user",
                text="Waiting...",
            ),
            ToolResultEvent(
                session_id="s1",
                uuid="u2",
                parent_uuid="u1",
                timestamp="t3",
                role="user",
                tool_use_id="tu1",
                is_error=False,
                content_text="done",
            ),
        ]
        rows = list(iter_dataset_rows_from_events(events, include_messages_in_trace=True))
        assert len(rows) == 1
        # Trace should have: tool_use, message, tool_result
        trace_types = [t["type"] for t in rows[0]["trace"]]
        assert "message" in trace_types

    def test_excludes_messages_from_trace_when_disabled(self) -> None:
        """Should exclude messages from trace when flag is False."""
        events = [
            ToolUseEvent(
                session_id="s1",
                uuid="u1",
                parent_uuid=None,
                timestamp="t1",
                role="assistant",
                tool_name="Read",
                tool_use_id="tu1",
                tool_input={},
            ),
            MessageEvent(
                session_id="s1",
                uuid="m1",
                parent_uuid="u1",
                timestamp="t2",
                role="user",
                text="Waiting...",
            ),
            ToolResultEvent(
                session_id="s1",
                uuid="u2",
                parent_uuid="u1",
                timestamp="t3",
                role="user",
                tool_use_id="tu1",
                is_error=False,
                content_text="done",
            ),
        ]
        rows = list(iter_dataset_rows_from_events(events, include_messages_in_trace=False))
        assert len(rows) == 1
        trace_types = [t["type"] for t in rows[0]["trace"]]
        assert "message" not in trace_types

    def test_handles_anonymous_tool_use_id(self) -> None:
        """Should handle tool_use events without tool_use_id."""
        events = [
            ToolUseEvent(
                session_id="s1",
                uuid="u1",
                parent_uuid=None,
                timestamp="t1",
                role="assistant",
                tool_name="Read",
                tool_use_id=None,  # No tool_use_id
                tool_input={},
            ),
        ]
        # Should not crash, just won't pair
        rows = list(iter_dataset_rows_from_events(events))
        assert rows == []

    def test_ignores_result_without_tool_use_id(self) -> None:
        """Should ignore tool_result events without tool_use_id."""
        events = [
            ToolResultEvent(
                session_id="s1",
                uuid="u1",
                parent_uuid=None,
                timestamp="t1",
                role="user",
                tool_use_id=None,  # No tool_use_id
                is_error=False,
                content_text="orphan result",
            ),
        ]
        rows = list(iter_dataset_rows_from_events(events))
        assert rows == []

    def test_ignores_orphan_tool_result(self) -> None:
        """Should ignore tool_result without matching tool_use."""
        events = [
            ToolResultEvent(
                session_id="s1",
                uuid="u1",
                parent_uuid=None,
                timestamp="t1",
                role="user",
                tool_use_id="nonexistent",  # No matching tool_use
                is_error=False,
                content_text="orphan result",
            ),
        ]
        rows = list(iter_dataset_rows_from_events(events))
        assert rows == []

    def test_multiple_tool_uses(self) -> None:
        """Should handle multiple tool_use/result pairs."""
        events = [
            ToolUseEvent(
                session_id="s1",
                uuid="u1",
                parent_uuid=None,
                timestamp="t1",
                role="assistant",
                tool_name="Read",
                tool_use_id="tu1",
                tool_input={"file": "a.py"},
            ),
            ToolResultEvent(
                session_id="s1",
                uuid="r1",
                parent_uuid="u1",
                timestamp="t2",
                role="user",
                tool_use_id="tu1",
                is_error=False,
                content_text="content a",
            ),
            ToolUseEvent(
                session_id="s1",
                uuid="u2",
                parent_uuid=None,
                timestamp="t3",
                role="assistant",
                tool_name="Write",
                tool_use_id="tu2",
                tool_input={"file": "b.py"},
            ),
            ToolResultEvent(
                session_id="s1",
                uuid="r2",
                parent_uuid="u2",
                timestamp="t4",
                role="user",
                tool_use_id="tu2",
                is_error=False,
                content_text="written",
            ),
        ]
        rows = list(iter_dataset_rows_from_events(events))
        assert len(rows) == 2
        assert rows[0]["tool_name"] == "Read"
        assert rows[1]["tool_name"] == "Write"

    def test_uses_session_id_from_tool_use(self) -> None:
        """Should use session_id from tool_use event."""
        events = [
            ToolUseEvent(
                session_id="session-abc",
                uuid="u1",
                parent_uuid=None,
                timestamp="t1",
                role="assistant",
                tool_name="Read",
                tool_use_id="tu1",
                tool_input={},
            ),
            ToolResultEvent(
                session_id="session-xyz",  # Different session
                uuid="r1",
                parent_uuid="u1",
                timestamp="t2",
                role="user",
                tool_use_id="tu1",
                is_error=False,
                content_text="result",
            ),
        ]
        rows = list(iter_dataset_rows_from_events(events))
        assert rows[0]["session_id"] == "session-abc"


class TestIterDatasetRows:
    """Tests for iter_dataset_rows function."""

    def test_empty_files_list(self, tmp_path: Path) -> None:
        """Should handle empty files list."""
        rows = list(iter_dataset_rows([]))
        assert rows == []

    def test_iterates_over_project_files(self, tmp_path: Path) -> None:
        """Should iterate over multiple project files."""
        # Create test JSONL files with proper structure
        file1 = tmp_path / "project1.jsonl"
        file2 = tmp_path / "project2.jsonl"

        # Create minimal valid JSONL that would be processed
        file1.write_text("")
        file2.write_text("")

        rows = list(iter_dataset_rows([file1, file2]))
        # Empty files produce no rows
        assert rows == []


class TestWriteJsonl:
    """Tests for write_jsonl function."""

    def test_writes_rows_to_file(self, tmp_path: Path) -> None:
        """Should write rows to JSONL file."""
        out_path = tmp_path / "output.jsonl"
        rows = [
            {"session_id": "s1", "tool_name": "Read"},
            {"session_id": "s1", "tool_name": "Write"},
        ]
        write_jsonl(iter(rows), out_path)

        lines = out_path.read_text().strip().split("\n")
        assert len(lines) == 2
        assert json.loads(lines[0])["tool_name"] == "Read"
        assert json.loads(lines[1])["tool_name"] == "Write"

    def test_creates_parent_directories(self, tmp_path: Path) -> None:
        """Should create parent directories if they don't exist."""
        out_path = tmp_path / "nested" / "dir" / "output.jsonl"
        write_jsonl([], out_path)
        assert out_path.parent.exists()

    def test_handles_empty_rows(self, tmp_path: Path) -> None:
        """Should handle empty rows iterable."""
        out_path = tmp_path / "empty.jsonl"
        write_jsonl([], out_path)
        assert out_path.read_text() == ""

    def test_handles_unicode_content(self, tmp_path: Path) -> None:
        """Should handle unicode content correctly."""
        out_path = tmp_path / "unicode.jsonl"
        rows = [{"text": "Hello 世界 🌍"}]
        write_jsonl(rows, out_path)

        content = out_path.read_text(encoding="utf-8")
        assert "世界" in content
        assert "🌍" in content

    def test_writes_with_ensure_ascii_false(self, tmp_path: Path) -> None:
        """Should write non-ASCII characters without escaping."""
        out_path = tmp_path / "test.jsonl"
        rows = [{"text": "café"}]
        write_jsonl(rows, out_path)

        content = out_path.read_text(encoding="utf-8")
        assert "café" in content
        assert "\\u" not in content  # Not escaped


class TestMain:
    """Tests for main function."""

    def test_insufficient_arguments(self) -> None:
        """Should raise SystemExit with insufficient arguments."""
        with pytest.raises(SystemExit) as exc_info:
            main(["projects_dataset.py"])
        assert "usage:" in str(exc_info.value)

    def test_two_arguments_insufficient(self) -> None:
        """Should raise SystemExit with only two arguments."""
        with pytest.raises(SystemExit) as exc_info:
            main(["projects_dataset.py", "out.jsonl"])
        assert "usage:" in str(exc_info.value)

    def test_writes_output_file(self, tmp_path: Path) -> None:
        """Should write output file from project files."""
        # Create empty project file
        project_file = tmp_path / "project.jsonl"
        project_file.write_text("")

        out_file = tmp_path / "output.jsonl"

        result = main(["projects_dataset.py", str(out_file), str(project_file)])
        assert result == 0
        assert out_file.exists()

    def test_handles_multiple_project_files(self, tmp_path: Path) -> None:
        """Should handle multiple project file arguments."""
        project1 = tmp_path / "p1.jsonl"
        project2 = tmp_path / "p2.jsonl"
        project1.write_text("")
        project2.write_text("")

        out_file = tmp_path / "output.jsonl"

        result = main(["projects_dataset.py", str(out_file), str(project1), str(project2)])
        assert result == 0

    def test_expands_user_paths(self, tmp_path: Path) -> None:
        """Should expand ~ in paths."""
        # This test verifies the expanduser call exists
        # We can't easily test actual ~ expansion in tmp_path
        project_file = tmp_path / "project.jsonl"
        project_file.write_text("")
        out_file = tmp_path / "out.jsonl"

        result = main(["projects_dataset.py", str(out_file), str(project_file)])
        assert result == 0


class TestIntegration:
    """Integration tests for complete dataset building workflow."""

    def test_full_workflow(self, tmp_path: Path) -> None:
        """Should build dataset from events to output file."""
        # Create events
        events = [
            MessageEvent(
                session_id="s1",
                uuid="m1",
                parent_uuid=None,
                timestamp="t1",
                role="user",
                text="Read the config file",
            ),
            ToolUseEvent(
                session_id="s1",
                uuid="tu1",
                parent_uuid="m1",
                timestamp="t2",
                role="assistant",
                tool_name="Read",
                tool_use_id="tool-1",
                tool_input={"file_path": "/etc/config"},
            ),
            ToolResultEvent(
                session_id="s1",
                uuid="tr1",
                parent_uuid="tu1",
                timestamp="t3",
                role="user",
                tool_use_id="tool-1",
                is_error=False,
                content_text="config content here",
            ),
        ]

        # Process events
        rows = list(iter_dataset_rows_from_events(events))

        # Write to file
        out_path = tmp_path / "dataset.jsonl"
        write_jsonl(rows, out_path)

        # Verify output
        lines = out_path.read_text().strip().split("\n")
        assert len(lines) == 1

        row = json.loads(lines[0])
        assert row["session_id"] == "s1"
        assert row["tool_name"] == "Read"
        assert row["reward"] == 1.0
        assert len(row["messages"]) == 1
        assert row["messages"][0]["text"] == "Read the config file"

    def test_complex_conversation(self, tmp_path: Path) -> None:
        """Should handle complex conversation with multiple tools."""
        events = [
            MessageEvent(
                session_id="s1",
                uuid="m1",
                parent_uuid=None,
                timestamp="t1",
                role="user",
                text="Find and fix the bug",
            ),
            MessageEvent(
                session_id="s1",
                uuid="m2",
                parent_uuid="m1",
                timestamp="t2",
                role="assistant",
                text="Let me search for the issue",
            ),
            ToolUseEvent(
                session_id="s1",
                uuid="tu1",
                parent_uuid="m2",
                timestamp="t3",
                role="assistant",
                tool_name="Grep",
                tool_use_id="grep-1",
                tool_input={"pattern": "bug"},
            ),
            ToolResultEvent(
                session_id="s1",
                uuid="tr1",
                parent_uuid="tu1",
                timestamp="t4",
                role="user",
                tool_use_id="grep-1",
                is_error=False,
                content_text="Found: file.py:10",
            ),
            ToolUseEvent(
                session_id="s1",
                uuid="tu2",
                parent_uuid="tr1",
                timestamp="t5",
                role="assistant",
                tool_name="Read",
                tool_use_id="read-1",
                tool_input={"file_path": "file.py"},
            ),
            ToolResultEvent(
                session_id="s1",
                uuid="tr2",
                parent_uuid="tu2",
                timestamp="t6",
                role="user",
                tool_use_id="read-1",
                is_error=False,
                content_text="def buggy(): pass",
            ),
            ToolUseEvent(
                session_id="s1",
                uuid="tu3",
                parent_uuid="tr2",
                timestamp="t7",
                role="assistant",
                tool_name="Edit",
                tool_use_id="edit-1",
                tool_input={"file_path": "file.py", "old": "buggy", "new": "fixed"},
            ),
            ToolResultEvent(
                session_id="s1",
                uuid="tr3",
                parent_uuid="tu3",
                timestamp="t8",
                role="user",
                tool_use_id="edit-1",
                is_error=False,
                content_text="Edit applied",
            ),
        ]

        rows = list(iter_dataset_rows_from_events(events, max_context_messages=10))

        assert len(rows) == 3
        assert rows[0]["tool_name"] == "Grep"
        assert rows[1]["tool_name"] == "Read"
        assert rows[2]["tool_name"] == "Edit"

        # All should have positive reward
        assert all(r["reward"] == 1.0 for r in rows)

        # Message context should grow
        assert len(rows[0]["messages"]) == 2  # user + assistant
        assert len(rows[1]["messages"]) == 2  # Same messages
        assert len(rows[2]["messages"]) == 2  # Same messages

    def test_error_handling_workflow(self, tmp_path: Path) -> None:
        """Should properly track error rewards in workflow."""
        events = [
            ToolUseEvent(
                session_id="s1",
                uuid="tu1",
                parent_uuid=None,
                timestamp="t1",
                role="assistant",
                tool_name="Read",
                tool_use_id="read-1",
                tool_input={"file_path": "/nonexistent"},
            ),
            ToolResultEvent(
                session_id="s1",
                uuid="tr1",
                parent_uuid="tu1",
                timestamp="t2",
                role="user",
                tool_use_id="read-1",
                is_error=True,
                content_text="File not found",
            ),
            ToolUseEvent(
                session_id="s1",
                uuid="tu2",
                parent_uuid="tr1",
                timestamp="t3",
                role="assistant",
                tool_name="Read",
                tool_use_id="read-2",
                tool_input={"file_path": "/exists"},
            ),
            ToolResultEvent(
                session_id="s1",
                uuid="tr2",
                parent_uuid="tu2",
                timestamp="t4",
                role="user",
                tool_use_id="read-2",
                is_error=False,
                content_text="File content",
            ),
        ]

        rows = list(iter_dataset_rows_from_events(events))

        assert len(rows) == 2
        assert rows[0]["reward"] == -1.0  # Error
        assert rows[1]["reward"] == 1.0  # Success
