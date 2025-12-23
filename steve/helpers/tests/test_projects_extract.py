"""Tests for projects_extract.py - JSONL event extraction from Claude projects."""

import dataclasses
import json
import sys
from pathlib import Path

import pytest


# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from projects_extract import (
    MessageEvent,
    NormalizedEvent,
    ToolResultEvent,
    ToolUseEvent,
    _extract_text_from_message,
    _get_str,
    extract_events,
    iter_jsonl,
    iter_project_events,
    iter_project_files,
)


class TestGetStr:
    """Tests for _get_str helper function."""

    def test_returns_string_value(self) -> None:
        """Should return string value for string key."""
        d = {"key": "value"}
        assert _get_str(d, "key") == "value"

    def test_returns_none_for_missing_key(self) -> None:
        """Should return None for missing key."""
        d = {"key": "value"}
        assert _get_str(d, "missing") is None

    def test_returns_none_for_non_string_value(self) -> None:
        """Should return None for non-string values."""
        d = {"int": 42, "list": [1, 2], "dict": {"a": 1}, "none": None}
        assert _get_str(d, "int") is None
        assert _get_str(d, "list") is None
        assert _get_str(d, "dict") is None
        assert _get_str(d, "none") is None

    def test_returns_empty_string(self) -> None:
        """Should return empty string if that's the value."""
        d = {"empty": ""}
        assert _get_str(d, "empty") == ""


class TestExtractTextFromMessage:
    """Tests for _extract_text_from_message helper function."""

    def test_returns_string_directly(self) -> None:
        """Should return string message directly."""
        assert _extract_text_from_message("hello world") == "hello world"

    def test_extracts_from_dict_with_string_content(self) -> None:
        """Should extract content from dict with string content."""
        msg = {"role": "user", "content": "hello world"}
        assert _extract_text_from_message(msg) == "hello world"

    def test_extracts_from_dict_with_list_content(self) -> None:
        """Should extract text items from list content."""
        msg = {
            "role": "assistant",
            "content": [
                {"type": "text", "text": "Hello"},
                {"type": "text", "text": "World"},
            ],
        }
        assert _extract_text_from_message(msg) == "Hello\nWorld"

    def test_ignores_non_text_items_in_list(self) -> None:
        """Should ignore non-text items in list content."""
        msg = {
            "role": "assistant",
            "content": [
                {"type": "text", "text": "Hello"},
                {"type": "tool_use", "name": "Read"},
                {"type": "text", "text": "World"},
            ],
        }
        assert _extract_text_from_message(msg) == "Hello\nWorld"

    def test_handles_empty_text_items(self) -> None:
        """Should skip empty text items."""
        msg = {
            "role": "assistant",
            "content": [
                {"type": "text", "text": "Hello"},
                {"type": "text", "text": ""},
                {"type": "text", "text": "World"},
            ],
        }
        assert _extract_text_from_message(msg) == "Hello\nWorld"

    def test_returns_empty_for_invalid_input(self) -> None:
        """Should return empty string for invalid input types."""
        assert _extract_text_from_message(None) == ""
        assert _extract_text_from_message(42) == ""
        assert _extract_text_from_message([1, 2, 3]) == ""

    def test_strips_result(self) -> None:
        """Should strip whitespace from result."""
        msg = {
            "content": [
                {"type": "text", "text": "  Hello  "},
            ]
        }
        result = _extract_text_from_message(msg)
        assert result == "Hello"


class TestIterJsonl:
    """Tests for iter_jsonl function."""

    def test_reads_valid_jsonl(self, tmp_path: Path) -> None:
        """Should read valid JSONL file."""
        jsonl_file = tmp_path / "test.jsonl"
        lines = [
            json.dumps({"id": 1, "name": "first"}),
            json.dumps({"id": 2, "name": "second"}),
        ]
        jsonl_file.write_text("\n".join(lines))

        results = list(iter_jsonl(jsonl_file))
        assert len(results) == 2
        assert results[0] == {"id": 1, "name": "first"}
        assert results[1] == {"id": 2, "name": "second"}

    def test_skips_empty_lines(self, tmp_path: Path) -> None:
        """Should skip empty lines."""
        jsonl_file = tmp_path / "test.jsonl"
        content = '{"id": 1}\n\n{"id": 2}\n   \n{"id": 3}'
        jsonl_file.write_text(content)

        results = list(iter_jsonl(jsonl_file))
        assert len(results) == 3

    def test_skips_invalid_json_lines(self, tmp_path: Path) -> None:
        """Should skip invalid JSON lines."""
        jsonl_file = tmp_path / "test.jsonl"
        content = '{"valid": true}\nnot json\n{"also_valid": true}'
        jsonl_file.write_text(content)

        results = list(iter_jsonl(jsonl_file))
        assert len(results) == 2
        assert results[0]["valid"] is True
        assert results[1]["also_valid"] is True

    def test_skips_non_dict_json(self, tmp_path: Path) -> None:
        """Should skip JSON that isn't a dict."""
        jsonl_file = tmp_path / "test.jsonl"
        content = '{"dict": true}\n[1, 2, 3]\n"string"\n42\n{"another": "dict"}'
        jsonl_file.write_text(content)

        results = list(iter_jsonl(jsonl_file))
        assert len(results) == 2

    def test_handles_empty_file(self, tmp_path: Path) -> None:
        """Should handle empty file."""
        jsonl_file = tmp_path / "empty.jsonl"
        jsonl_file.write_text("")

        results = list(iter_jsonl(jsonl_file))
        assert results == []

    def test_handles_unicode(self, tmp_path: Path) -> None:
        """Should handle unicode characters."""
        jsonl_file = tmp_path / "unicode.jsonl"
        jsonl_file.write_text('{"text": "Hello 世界 🌍"}')

        results = list(iter_jsonl(jsonl_file))
        assert results[0]["text"] == "Hello 世界 🌍"


class TestExtractEvents:
    """Tests for extract_events function."""

    def test_skips_meta_records(self) -> None:
        """Should skip records with isMeta=True."""
        record = {"type": "message", "isMeta": True, "message": {"role": "user"}}
        events = extract_events(record)
        assert events == []

    def test_skips_internal_record_types(self) -> None:
        """Should skip internal record types."""
        for record_type in ["file-history-snapshot", "queue-operation", "summary"]:
            record = {"type": record_type}
            events = extract_events(record)
            assert events == []

    def test_extracts_tool_use_event(self) -> None:
        """Should extract ToolUseEvent from assistant message."""
        record = {
            "sessionId": "session-123",
            "uuid": "uuid-456",
            "parentUuid": "parent-789",
            "timestamp": "2024-01-01T00:00:00Z",
            "message": {
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_use",
                        "name": "Read",
                        "id": "tool-id-1",
                        "input": {"file_path": "/test.txt"},
                    }
                ],
            },
        }
        events = extract_events(record)

        tool_events = [e for e in events if isinstance(e, ToolUseEvent)]
        assert len(tool_events) == 1
        assert tool_events[0].session_id == "session-123"
        assert tool_events[0].tool_name == "Read"
        assert tool_events[0].tool_use_id == "tool-id-1"
        assert tool_events[0].tool_input == {"file_path": "/test.txt"}

    def test_extracts_multiple_tool_use_events(self) -> None:
        """Should extract multiple ToolUseEvents from single message."""
        record = {
            "message": {
                "role": "assistant",
                "content": [
                    {"type": "tool_use", "name": "Read", "id": "id1", "input": {}},
                    {"type": "tool_use", "name": "Write", "id": "id2", "input": {}},
                ],
            }
        }
        events = extract_events(record)

        tool_events = [e for e in events if isinstance(e, ToolUseEvent)]
        assert len(tool_events) == 2
        assert tool_events[0].tool_name == "Read"
        assert tool_events[1].tool_name == "Write"

    def test_skips_tool_use_without_name(self) -> None:
        """Should skip tool_use without valid name."""
        record = {
            "message": {
                "role": "assistant",
                "content": [
                    {"type": "tool_use", "id": "id1", "input": {}},  # No name
                    {"type": "tool_use", "name": "", "id": "id2", "input": {}},  # Empty
                ],
            }
        }
        events = extract_events(record)
        tool_events = [e for e in events if isinstance(e, ToolUseEvent)]
        assert len(tool_events) == 0

    def test_handles_tool_use_without_id(self) -> None:
        """Should handle tool_use without id (sets to None)."""
        record = {
            "message": {
                "role": "assistant",
                "content": [
                    {"type": "tool_use", "name": "Read", "input": {}},
                ],
            }
        }
        events = extract_events(record)
        tool_events = [e for e in events if isinstance(e, ToolUseEvent)]
        assert len(tool_events) == 1
        assert tool_events[0].tool_use_id is None

    def test_handles_tool_use_with_non_dict_input(self) -> None:
        """Should handle tool_use with non-dict input."""
        record = {
            "message": {
                "role": "assistant",
                "content": [
                    {"type": "tool_use", "name": "Read", "id": "id1", "input": "string"},
                ],
            }
        }
        events = extract_events(record)
        tool_events = [e for e in events if isinstance(e, ToolUseEvent)]
        assert len(tool_events) == 1
        assert tool_events[0].tool_input == {}

    def test_extracts_tool_result_event(self) -> None:
        """Should extract ToolResultEvent from user message."""
        record = {
            "sessionId": "session-123",
            "uuid": "uuid-456",
            "timestamp": "2024-01-01T00:00:00Z",
            "message": {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": "tool-id-1",
                        "is_error": False,
                        "content": "File contents here",
                    }
                ],
            },
        }
        events = extract_events(record)

        result_events = [e for e in events if isinstance(e, ToolResultEvent)]
        assert len(result_events) == 1
        assert result_events[0].tool_use_id == "tool-id-1"
        assert result_events[0].is_error is False
        assert result_events[0].content_text == "File contents here"

    def test_extracts_tool_result_with_list_content(self) -> None:
        """Should extract text from list content in tool_result."""
        record = {
            "message": {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": "id1",
                        "content": [
                            {"type": "text", "text": "Line 1"},
                            {"type": "text", "text": "Line 2"},
                        ],
                    }
                ],
            },
        }
        events = extract_events(record)

        result_events = [e for e in events if isinstance(e, ToolResultEvent)]
        assert len(result_events) == 1
        assert result_events[0].content_text == "Line 1\nLine 2"

    def test_extracts_tool_result_with_error(self) -> None:
        """Should extract error flag from tool_result."""
        record = {
            "message": {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": "id1",
                        "is_error": True,
                        "content": "Error message",
                    }
                ],
            },
        }
        events = extract_events(record)

        result_events = [e for e in events if isinstance(e, ToolResultEvent)]
        assert len(result_events) == 1
        assert result_events[0].is_error is True

    def test_extracts_message_event(self) -> None:
        """Should extract MessageEvent from user/assistant message."""
        record = {
            "sessionId": "session-123",
            "uuid": "uuid-456",
            "parentUuid": "parent-789",
            "timestamp": "2024-01-01T00:00:00Z",
            "message": {
                "role": "user",
                "content": "Hello, Claude!",
            },
        }
        events = extract_events(record)

        msg_events = [e for e in events if isinstance(e, MessageEvent)]
        assert len(msg_events) == 1
        assert msg_events[0].session_id == "session-123"
        assert msg_events[0].role == "user"
        assert msg_events[0].text == "Hello, Claude!"

    def test_extracts_assistant_message_event(self) -> None:
        """Should extract MessageEvent from assistant."""
        record = {
            "message": {
                "role": "assistant",
                "content": "Hello! How can I help?",
            },
        }
        events = extract_events(record)

        msg_events = [e for e in events if isinstance(e, MessageEvent)]
        assert len(msg_events) == 1
        assert msg_events[0].role == "assistant"
        assert msg_events[0].text == "Hello! How can I help?"

    def test_skips_message_with_empty_text(self) -> None:
        """Should skip message events with empty text."""
        record = {
            "message": {
                "role": "user",
                "content": "",
            },
        }
        events = extract_events(record)
        msg_events = [e for e in events if isinstance(e, MessageEvent)]
        assert len(msg_events) == 0

    def test_handles_mixed_content(self) -> None:
        """Should extract both tool events and message from same record."""
        record = {
            "message": {
                "role": "assistant",
                "content": [
                    {"type": "text", "text": "Let me read that file."},
                    {"type": "tool_use", "name": "Read", "id": "id1", "input": {}},
                ],
            },
        }
        events = extract_events(record)

        assert len(events) == 2
        tool_events = [e for e in events if isinstance(e, ToolUseEvent)]
        msg_events = [e for e in events if isinstance(e, MessageEvent)]
        assert len(tool_events) == 1
        assert len(msg_events) == 1

    def test_handles_empty_record(self) -> None:
        """Should handle empty record."""
        events = extract_events({})
        assert events == []

    def test_handles_record_without_message(self) -> None:
        """Should handle record without message field."""
        record = {"type": "some_type", "sessionId": "123"}
        events = extract_events(record)
        assert events == []


class TestIterProjectEvents:
    """Tests for iter_project_events function."""

    def test_iterates_over_multiple_files(self, tmp_path: Path) -> None:
        """Should iterate events from multiple JSONL files."""
        file1 = tmp_path / "project1.jsonl"
        file2 = tmp_path / "project2.jsonl"

        file1.write_text(json.dumps({"message": {"role": "user", "content": "From file 1"}}))
        file2.write_text(json.dumps({"message": {"role": "user", "content": "From file 2"}}))

        events = list(iter_project_events([file1, file2]))
        assert len(events) == 2

    def test_yields_events_in_order(self, tmp_path: Path) -> None:
        """Should yield events in file order."""
        jsonl_file = tmp_path / "project.jsonl"
        lines = [
            json.dumps({"message": {"role": "user", "content": "First"}}),
            json.dumps({"message": {"role": "assistant", "content": "Second"}}),
        ]
        jsonl_file.write_text("\n".join(lines))

        events = list(iter_project_events([jsonl_file]))
        assert len(events) == 2
        assert events[0].text == "First"
        assert events[1].text == "Second"

    def test_handles_empty_file_list(self) -> None:
        """Should handle empty file list."""
        events = list(iter_project_events([]))
        assert events == []


class TestIterProjectFiles:
    """Tests for iter_project_files function."""

    def test_finds_jsonl_files(self, tmp_path: Path) -> None:
        """Should find all JSONL files recursively."""
        (tmp_path / "file1.jsonl").write_text("{}")
        (tmp_path / "subdir").mkdir()
        (tmp_path / "subdir" / "file2.jsonl").write_text("{}")

        files = list(iter_project_files(tmp_path))
        assert len(files) == 2
        filenames = [f.name for f in files]
        assert "file1.jsonl" in filenames
        assert "file2.jsonl" in filenames

    def test_ignores_non_jsonl_files(self, tmp_path: Path) -> None:
        """Should ignore non-JSONL files."""
        (tmp_path / "file.jsonl").write_text("{}")
        (tmp_path / "file.json").write_text("{}")
        (tmp_path / "file.txt").write_text("text")

        files = list(iter_project_files(tmp_path))
        assert len(files) == 1
        assert files[0].name == "file.jsonl"

    def test_handles_empty_directory(self, tmp_path: Path) -> None:
        """Should handle empty directory."""
        files = list(iter_project_files(tmp_path))
        assert files == []


class TestEventDataclasses:
    """Tests for event dataclass definitions."""

    def test_message_event_frozen(self) -> None:
        """MessageEvent should be frozen (immutable)."""
        event = MessageEvent(
            session_id="s1",
            uuid="u1",
            parent_uuid="p1",
            timestamp="t1",
            role="user",
            text="hello",
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            event.text = "modified"  # type: ignore[misc]

    def test_tool_use_event_frozen(self) -> None:
        """ToolUseEvent should be frozen (immutable)."""
        event = ToolUseEvent(
            session_id="s1",
            uuid="u1",
            parent_uuid="p1",
            timestamp="t1",
            role="assistant",
            tool_name="Read",
            tool_use_id="id1",
            tool_input={},
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            event.tool_name = "Write"  # type: ignore[misc]

    def test_tool_result_event_frozen(self) -> None:
        """ToolResultEvent should be frozen (immutable)."""
        event = ToolResultEvent(
            session_id="s1",
            uuid="u1",
            parent_uuid="p1",
            timestamp="t1",
            role="user",
            tool_use_id="id1",
            is_error=False,
            content_text="result",
        )
        with pytest.raises(dataclasses.FrozenInstanceError):
            event.is_error = True  # type: ignore[misc]

    def test_normalized_event_type_alias(self) -> None:
        """NormalizedEvent should be a union of all event types."""
        msg_event = MessageEvent(
            session_id=None,
            uuid=None,
            parent_uuid=None,
            timestamp=None,
            role="user",
            text="test",
        )
        tool_use = ToolUseEvent(
            session_id=None,
            uuid=None,
            parent_uuid=None,
            timestamp=None,
            role="assistant",
            tool_name="Read",
            tool_use_id=None,
            tool_input={},
        )
        tool_result = ToolResultEvent(
            session_id=None,
            uuid=None,
            parent_uuid=None,
            timestamp=None,
            role="user",
            tool_use_id=None,
            is_error=False,
            content_text="",
        )

        # All should be valid NormalizedEvent types
        events: list[NormalizedEvent] = [msg_event, tool_use, tool_result]
        assert len(events) == 3


class TestIntegration:
    """Integration tests for complete extraction workflow."""

    def test_full_conversation_extraction(self, tmp_path: Path) -> None:
        """Should extract complete conversation with tools."""
        jsonl_file = tmp_path / "conversation.jsonl"
        records = [
            {
                "sessionId": "session-1",
                "timestamp": "2024-01-01T00:00:00Z",
                "message": {"role": "user", "content": "Read my file"},
            },
            {
                "sessionId": "session-1",
                "timestamp": "2024-01-01T00:00:01Z",
                "message": {
                    "role": "assistant",
                    "content": [
                        {"type": "text", "text": "I'll read that for you."},
                        {
                            "type": "tool_use",
                            "name": "Read",
                            "id": "tool-1",
                            "input": {"file_path": "/test.txt"},
                        },
                    ],
                },
            },
            {
                "sessionId": "session-1",
                "timestamp": "2024-01-01T00:00:02Z",
                "message": {
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": "tool-1",
                            "content": "File contents here",
                        }
                    ],
                },
            },
        ]
        jsonl_file.write_text("\n".join(json.dumps(r) for r in records))

        events = list(iter_project_events([jsonl_file]))

        # Should have: user message, assistant message + tool use, tool result
        msg_events = [e for e in events if isinstance(e, MessageEvent)]
        tool_use_events = [e for e in events if isinstance(e, ToolUseEvent)]
        tool_result_events = [e for e in events if isinstance(e, ToolResultEvent)]

        assert len(msg_events) == 2  # user + assistant text
        assert len(tool_use_events) == 1
        assert len(tool_result_events) == 1

        assert msg_events[0].text == "Read my file"
        assert tool_use_events[0].tool_name == "Read"
        assert tool_result_events[0].content_text == "File contents here"
