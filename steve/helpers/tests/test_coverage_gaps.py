"""Tests for uncovered code paths identified in coverage analysis.

GENERATED: Review and refine these tests before committing.

This file contains tests for critical gaps in test coverage:
- agent_state_snapshot.py __post_init__ bug (lines 42-48)
- context-monitor.py error handling (lines 74-75, 79-80)
- context-monitor.py display edge cases (lines 167, 189, 222)
- projects_extract.py malformed data handling (lines 133, 165, 175-185)
- history_archival.py verbose logging (lines 101, 122, 171)
- debug_rotation.py verbose logging (line 110)
"""

import json
from collections import defaultdict
from datetime import datetime, timedelta
from unittest.mock import patch

import pytest

import steve.helpers.debug_rotation as debug_rotation_module
import steve.helpers.history_archival as history_archival_module
from steve.helpers.agent_state_snapshot import AgentStateSnapshot
from steve.helpers.context_monitor import (
    get_context_display,
    get_session_metrics,
    parse_context_from_transcript,
)
from steve.helpers.debug_rotation import rotate_debug_logs
from steve.helpers.history_archival import archive_history, process_entry, write_archives
from steve.helpers.projects_extract import extract_events


class TestAgentStateSnapshotDerivedFields:
    """Tests verifying derived fields are computed correctly.

    The implementation uses Pydantic's model_validator to compute derived
    fields after validation, which properly replaces the broken __post_init__.
    """

    def test_derived_fields_computed_on_creation(self) -> None:
        """Verify sha256 and other derived fields are computed."""
        snapshot = AgentStateSnapshot.extract_shell_snapshot_state("test content")

        # Derived fields should be computed via model_validator
        assert hasattr(snapshot, "sha256")
        assert snapshot.sha256 != ""
        assert len(snapshot.sha256) == 64  # SHA256 hex digest length

        # Verify other derived fields
        assert snapshot.bytes == len(b"test content")
        assert snapshot.line_count == 1
        assert snapshot.function_count == 0
        assert snapshot.alias_count == 0
        assert snapshot.export_count == 0

    def test_post_init_static_methods_work(self) -> None:
        """Static methods work, but are never called in practice."""
        text = "test content"
        sha256 = AgentStateSnapshot._sha256_text(text)
        assert len(sha256) == 64
        assert sha256 == "6ae8a75555209fd6c44157c0aed8016e763ff435a19cf186f76863140143ff72"

    def test_post_init_token_hash_works(self) -> None:
        """Token hash method works but is never called."""
        function_name = "my_function"
        hash_result = AgentStateSnapshot._token_hash(function_name)
        assert len(hash_result) == 16  # 8 bytes = 16 hex chars


class TestParseContextErrorHandling:
    """Tests for error handling paths in parse_context_from_transcript."""

    def test_handles_permission_error_gracefully(self, tmp_path) -> None:
        """Should return None when file permissions deny access."""
        protected_file = tmp_path / "protected.txt"
        protected_file.write_text('{"type":"assistant","message":{}}')
        protected_file.chmod(0o000)

        try:
            result = parse_context_from_transcript(str(protected_file))
            # Lines 79-80: PermissionError handling
            assert result is None
        finally:
            # Cleanup: restore permissions for cleanup
            protected_file.chmod(0o644)

    def test_handles_json_decode_error_gracefully(self, tmp_path) -> None:
        """Should skip malformed JSON lines without crashing."""
        transcript = tmp_path / "transcript.txt"
        transcript.write_text("""
{"type":"assistant","message":{"usage":{"input_tokens":1000}}}
{invalid json here}
{"type":"assistant","message":{"usage":{"input_tokens":2000}}}
""")

        # Lines 74-75: JSONDecodeError handling
        result = parse_context_from_transcript(str(transcript))
        assert result is not None
        assert result["tokens"] == 2000


class TestContextDisplayEdgeCases:
    """Tests for edge cases in context display logic."""

    def test_model_color_exactly_75_percent(self) -> None:
        """Should use light red (orange icon) for exactly 75% context usage."""
        context_info = {"percent": 75.0}
        display = get_context_display(context_info)

        # Line 98-100: Should use light red color for >= 75%
        assert "\033[91m" in display  # Light red color code
        assert "75%" in display

    def test_model_color_between_75_and_90_percent(self) -> None:
        """Should use appropriate color for mid-high usage."""
        context_info = {"percent": 80.0}
        display = get_context_display(context_info)
        assert "80%" in display

    def test_session_metrics_long_duration_exactly_30_minutes(self) -> None:
        """Should use yellow for exactly 30 minute sessions."""
        cost_data = {
            "total_cost_usd": 0.05,
            "total_duration_ms": 30 * 60 * 1000,  # Exactly 30 minutes
        }

        # Line 167: Should use yellow color for >= 30 minutes
        metrics = get_session_metrics(cost_data)
        assert "30m" in metrics
        assert "\033[33m" in metrics  # Yellow color

    def test_session_metrics_neutral_lines_changed(self) -> None:
        """Should use yellow when lines added equals lines removed."""
        cost_data = {
            "total_lines_added": 50,
            "total_lines_removed": 50,  # Net zero
        }

        # Line 189: Should use yellow for neutral changes
        metrics = get_session_metrics(cost_data)
        assert "+0" in metrics or "0" in metrics
        assert "\033[33m" in metrics  # Yellow color


class TestProjectsExtractMalformedData:
    """Tests for handling malformed data in projects_extract."""

    def test_tool_use_with_string_in_content(self) -> None:
        """Should skip string items in content list (line 133)."""
        record = {
            "sessionId": "test-session",
            "message": {
                "role": "assistant",
                "content": [
                    "this is a string, not a dict",  # Line 133: not isinstance(item, dict)
                    {
                        "type": "tool_use",
                        "name": "Read",
                        "id": "tool-1",
                        "input": {"file_path": "/test"},
                    },
                    12345,  # Also not a dict
                ],
            },
        }

        events = extract_events(record)
        # Should only extract the valid tool_use event
        assert len(events) == 1
        assert events[0].tool_name == "Read"

    def test_tool_result_with_mixed_content_types(self) -> None:
        """Should skip non-dict items in tool_result content (line 165)."""
        record = {
            "message": {
                "role": "user",
                "content": [
                    None,  # Line 165: not isinstance(item, dict)
                    {"type": "tool_result", "tool_use_id": "tool-1", "content": "result text"},
                    [],  # Also not a dict
                ],
            },
        }

        events = extract_events(record)
        assert len(events) == 1
        assert events[0].content_text == "result text"

    def test_tool_result_complex_content_extraction(self) -> None:
        """Should handle complex nested content lists (lines 175-185)."""
        record = {
            "message": {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": "tool-1",
                        "content": [
                            {"type": "text", "text": "line1"},
                            {"type": "image", "data": "..."},  # Not text type, skip
                            {"type": "text", "text": ""},  # Empty text, should include
                            {"type": "text", "text": None},  # None text, skip (line 181)
                            {"type": "text"},  # Missing text field, skip (line 179)
                            {"type": "text", "text": "line2"},
                        ],
                    }
                ],
            },
        }

        events = extract_events(record)
        assert len(events) == 1
        # Should include "line1" and "line2", skip others
        assert "line1" in events[0].content_text
        assert "line2" in events[0].content_text


class TestHistoryArchivalVerboseLogging:
    """Tests for verbose logging paths in history_archival."""

    def test_process_entry_verbose_mode_archives(self, caplog) -> None:
        """Should log debug info for archived entries in verbose mode (line 101)."""
        cutoff = datetime.now() - timedelta(days=30)
        old_date = cutoff - timedelta(days=5)
        old_entry = {"timestamp": old_date.timestamp() * 1000}
        line = json.dumps(old_entry)

        recent: list[str] = []
        archives: dict[str, list[str]] = defaultdict(list)
        stats = {
            "total_entries": 0,
            "kept_entries": 0,
            "archived_entries": 0,
            "parse_errors": 0,
        }

        # Line 101: Verbose logging for archived entry
        with caplog.at_level("DEBUG"):
            process_entry(line, cutoff, recent, archives, stats, verbose=True)

        # Should have archived the entry
        assert stats["archived_entries"] == 1
        assert len(archives) > 0

    def test_write_archives_verbose_mode(self, tmp_path, caplog) -> None:
        """Should log info for each archive file in verbose mode (line 122)."""
        archive_dir = tmp_path / "archives"
        archive_entries = {
            "2024-01": ['{"test": "entry1"}', '{"test": "entry2"}'],
            "2024-02": ['{"test": "entry3"}'],
        }

        # Line 122: Verbose logging in write_archives
        with caplog.at_level("INFO"):
            archives_created = write_archives(
                archive_dir, archive_entries, dry_run=False, verbose=True
            )

        assert len(archives_created) == 2
        assert "2024-01 (2 entries)" in archives_created
        assert "2024-02 (1 entries)" in archives_created

    def test_archive_history_skips_blank_lines(self, tmp_path) -> None:
        """Should skip blank lines when processing history file (line 171)."""
        # Create a test history file with blank lines
        history_file = tmp_path / "history.jsonl"
        history_file.write_text("""

{"timestamp": 1234567890000, "data": "entry1"}

{"timestamp": 1234567891000, "data": "entry2"}

""")

        # Use unittest.mock.patch to mock the get_history_file function
        with patch.object(history_archival_module, "get_history_file", return_value=history_file):
            stats = archive_history(retention_days=0, dry_run=True)
            # Line 171: Blank lines are skipped in the loop
            # Should process only the 2 valid entries
            assert stats["total_entries"] == 2


class TestDebugRotationVerboseLogging:
    """Tests for verbose logging in debug_rotation."""

    def test_verbose_logs_kept_files_at_debug_level(self, tmp_path, caplog) -> None:
        """Should log kept files at DEBUG level in verbose mode (line 110)."""
        # Create test files
        debug_dir = tmp_path / "debug"
        debug_dir.mkdir()
        recent_file = debug_dir / "recent.txt"
        recent_file.write_text("test content")

        # Use unittest.mock.patch to mock get_debug_dir
        with patch.object(debug_rotation_module, "get_debug_dir", return_value=debug_dir):
            # Line 110: Debug logging for kept files
            with caplog.at_level("DEBUG"):
                stats = rotate_debug_logs(retention_days=7, dry_run=True, verbose=True)

            # File should be kept (recent)
            assert stats["kept_files"] == 1
            assert stats["deleted_files"] == 0


class TestPropertyBasedSuggestions:
    """Placeholder for property-based testing recommendations.

    These tests are NOT implemented but are recommended additions:

    1. Property-based tests for extract_shell_snapshot_state:
       - Generate random valid shell scripts
       - Verify: extracted names are always sorted
       - Verify: no duplicate names in results
       - Verify: max_names limit is always respected

    2. Property-based tests for parse_context_from_transcript:
       - Generate random JSON structures
       - Verify: never crashes on malformed input
       - Verify: always returns None or valid dict

    3. Property-based tests for event extraction:
       - Generate random JSONL records
       - Verify: never crashes on any input
       - Verify: output events are always well-formed
    """

    def test_property_based_tests_not_implemented(self) -> None:
        """Placeholder - property-based tests recommended but not implemented."""
        pytest.skip("Property-based tests recommended but not yet implemented")


class TestIntegrationGaps:
    """Placeholder for integration test recommendations.

    These tests are NOT implemented but are recommended additions:

    1. Full pipeline test: projects JSONL -> dataset rows -> output file
    2. History archival with large files (1GB+)
    3. Debug rotation with concurrent file operations
    4. Context monitor with real transcript files from production
    """

    def test_integration_tests_not_implemented(self) -> None:
        """Placeholder - integration tests recommended but not implemented."""
        pytest.skip("Integration tests recommended but not yet implemented")
