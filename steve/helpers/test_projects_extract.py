# /// script
# requires-python = ">=3.12"
# ///
"""Tests for projects_extract module."""

from steve.helpers.projects_extract import (
    MessageEvent,
    ToolResultEvent,
    ToolUseEvent,
    extract_events,
)


class TestProjectsExtract:
    def test_extracts_tool_use(self) -> None:
        rec = {
            "type": "assistant",
            "sessionId": "S",
            "uuid": "U",
            "parentUuid": "P",
            "timestamp": "2025-01-01T00:00:00Z",
            "message": {
                "role": "assistant",
                "content": [
                    {
                        "type": "tool_use",
                        "id": "toolu_123",
                        "name": "Read",
                        "input": {"path": "/example/file.txt"},
                    }
                ],
            },
        }
        evs = extract_events(rec)
        tus = [e for e in evs if isinstance(e, ToolUseEvent)]
        assert len(tus) == 1
        assert tus[0].tool_name == "Read"
        assert tus[0].tool_use_id == "toolu_123"
        assert tus[0].tool_input == {"path": "/example/file.txt"}

    def test_extracts_tool_result(self) -> None:
        rec = {
            "type": "user",
            "sessionId": "S",
            "uuid": "U",
            "parentUuid": "P",
            "timestamp": "2025-01-01T00:00:00Z",
            "message": {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": "toolu_123",
                        "is_error": True,
                        "content": [{"type": "text", "text": "boom"}],
                    }
                ],
            },
        }
        evs = extract_events(rec)
        trs = [e for e in evs if isinstance(e, ToolResultEvent)]
        assert len(trs) == 1
        assert trs[0].is_error is True
        assert trs[0].tool_use_id == "toolu_123"
        assert trs[0].content_text == "boom"

    def test_extracts_plain_text_message(self) -> None:
        rec = {
            "type": "user",
            "sessionId": "S",
            "uuid": "U",
            "parentUuid": "P",
            "timestamp": "2025-01-01T00:00:00Z",
            "message": {"role": "user", "content": "hello"},
        }
        evs = extract_events(rec)
        msgs = [e for e in evs if isinstance(e, MessageEvent)]
        assert len(msgs) == 1
        assert msgs[0].text == "hello"
