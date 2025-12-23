"""Tests for context-monitor.py - Claude Code context usage monitoring."""

import json
import sys
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest


# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import must happen after path modification
# Rename import since filename has hyphen
import importlib.util


spec = importlib.util.spec_from_file_location(
    "context_monitor",
    Path(__file__).parent.parent / "context_monitor.py",
)
context_monitor = importlib.util.module_from_spec(spec)
spec.loader.exec_module(context_monitor)


class TestParseContextFromTranscript:
    """Tests for parse_context_from_transcript function."""

    def test_returns_none_for_nonexistent_file(self) -> None:
        """Should return None when file doesn't exist."""
        result = context_monitor.parse_context_from_transcript("/nonexistent/path.jsonl")
        assert result is None

    def test_returns_none_for_none_path(self) -> None:
        """Should return None when path is None."""
        result = context_monitor.parse_context_from_transcript(None)
        assert result is None

    def test_returns_none_for_empty_path(self) -> None:
        """Should return None when path is empty string."""
        result = context_monitor.parse_context_from_transcript("")
        assert result is None

    def test_parses_usage_tokens(self, tmp_path: Path) -> None:
        """Should parse context usage from assistant message usage data."""
        transcript = tmp_path / "transcript.jsonl"
        entry = {
            "type": "assistant",
            "message": {
                "usage": {
                    "input_tokens": 50000,
                    "cache_read_input_tokens": 10000,
                    "cache_creation_input_tokens": 5000,
                }
            },
        }
        transcript.write_text(json.dumps(entry) + "\n")

        result = context_monitor.parse_context_from_transcript(str(transcript))

        assert result is not None
        assert result["method"] == "usage"
        # Total tokens = 50000 + 10000 + 5000 = 65000
        # Percent = (65000 / 200000) * 100 = 32.5%
        assert result["percent"] == pytest.approx(32.5, rel=0.01)
        assert result["tokens"] == 65000

    def test_parses_auto_compact_warning(self, tmp_path: Path) -> None:
        """Should parse auto-compact system warning."""
        transcript = tmp_path / "transcript.jsonl"
        entry = {
            "type": "system_message",
            "content": "Context left until auto-compact: 15%",
        }
        transcript.write_text(json.dumps(entry) + "\n")

        result = context_monitor.parse_context_from_transcript(str(transcript))

        assert result is not None
        assert result["method"] == "system"
        assert result["warning"] == "auto-compact"
        assert result["percent"] == 85  # 100 - 15

    def test_parses_context_low_warning(self, tmp_path: Path) -> None:
        """Should parse context low system warning."""
        transcript = tmp_path / "transcript.jsonl"
        entry = {
            "type": "system_message",
            "content": "Context low (20% remaining)",
        }
        transcript.write_text(json.dumps(entry) + "\n")

        result = context_monitor.parse_context_from_transcript(str(transcript))

        assert result is not None
        assert result["method"] == "system"
        assert result["warning"] == "low"
        assert result["percent"] == 80  # 100 - 20

    def test_returns_none_for_empty_file(self, tmp_path: Path) -> None:
        """Should return None for empty transcript file."""
        transcript = tmp_path / "transcript.jsonl"
        transcript.write_text("")

        result = context_monitor.parse_context_from_transcript(str(transcript))
        assert result is None

    def test_returns_none_for_no_context_data(self, tmp_path: Path) -> None:
        """Should return None when no context data found."""
        transcript = tmp_path / "transcript.jsonl"
        entry = {"type": "user", "content": "Hello"}
        transcript.write_text(json.dumps(entry) + "\n")

        result = context_monitor.parse_context_from_transcript(str(transcript))
        assert result is None

    def test_skips_malformed_json_lines(self, tmp_path: Path) -> None:
        """Should skip malformed JSON lines and continue parsing."""
        transcript = tmp_path / "transcript.jsonl"
        lines = [
            "not valid json",
            json.dumps({"type": "system_message", "content": "Context low (25% remaining)"}),
        ]
        transcript.write_text("\n".join(lines) + "\n")

        result = context_monitor.parse_context_from_transcript(str(transcript))

        assert result is not None
        assert result["percent"] == 75

    def test_checks_only_last_15_lines(self, tmp_path: Path) -> None:
        """Should only check the last 15 lines for context info."""
        transcript = tmp_path / "transcript.jsonl"

        # Old context warning (should be ignored - more than 15 lines back)
        lines = [json.dumps({"type": "system_message", "content": "Context low (5% remaining)"})]
        # Add 20 non-context lines
        lines.extend(json.dumps({"type": "user", "content": f"message {i}"}) for i in range(20))

        transcript.write_text("\n".join(lines) + "\n")

        result = context_monitor.parse_context_from_transcript(str(transcript))
        # Should not find the old context warning
        assert result is None

    def test_caps_percent_at_100(self, tmp_path: Path) -> None:
        """Should cap percentage at 100 even with high token counts."""
        transcript = tmp_path / "transcript.jsonl"
        entry = {
            "type": "assistant",
            "message": {
                "usage": {
                    "input_tokens": 300000,  # Over the 200k limit
                    "cache_read_input_tokens": 0,
                    "cache_creation_input_tokens": 0,
                }
            },
        }
        transcript.write_text(json.dumps(entry) + "\n")

        result = context_monitor.parse_context_from_transcript(str(transcript))

        assert result is not None
        assert result["percent"] == 100  # Capped at 100

    def test_skips_zero_token_usage(self, tmp_path: Path) -> None:
        """Should skip entries with zero total tokens."""
        transcript = tmp_path / "transcript.jsonl"
        lines = [
            json.dumps(
                {
                    "type": "assistant",
                    "message": {
                        "usage": {
                            "input_tokens": 0,
                            "cache_read_input_tokens": 0,
                            "cache_creation_input_tokens": 0,
                        }
                    },
                }
            ),
            json.dumps({"type": "system_message", "content": "Context low (30% remaining)"}),
        ]
        transcript.write_text("\n".join(lines) + "\n")

        result = context_monitor.parse_context_from_transcript(str(transcript))

        assert result is not None
        assert result["percent"] == 70  # Found the system message instead


class TestGetContextDisplay:
    """Tests for get_context_display function."""

    def test_returns_unknown_for_none(self) -> None:
        """Should return unknown indicator for None context info."""
        result = context_monitor.get_context_display(None)
        assert "???" in result

    def test_green_for_low_usage(self) -> None:
        """Should show green indicator for low usage."""
        result = context_monitor.get_context_display({"percent": 30})
        assert "🟢" in result
        assert "30%" in result

    def test_yellow_for_moderate_usage(self) -> None:
        """Should show yellow indicator for moderate usage."""
        result = context_monitor.get_context_display({"percent": 55})
        assert "🟡" in result
        assert "55%" in result

    def test_orange_for_high_usage(self) -> None:
        """Should show orange indicator for high usage."""
        result = context_monitor.get_context_display({"percent": 80})
        assert "🟠" in result
        assert "80%" in result

    def test_red_for_very_high_usage(self) -> None:
        """Should show red indicator for very high usage."""
        result = context_monitor.get_context_display({"percent": 92})
        assert "🔴" in result
        assert "92%" in result
        assert "HIGH" in result

    def test_critical_for_extreme_usage(self) -> None:
        """Should show critical indicator for extreme usage."""
        result = context_monitor.get_context_display({"percent": 97})
        assert "🚨" in result
        assert "97%" in result
        assert "CRIT" in result

    def test_auto_compact_warning(self) -> None:
        """Should show auto-compact warning."""
        result = context_monitor.get_context_display({"percent": 85, "warning": "auto-compact"})
        assert "AUTO-COMPACT!" in result

    def test_low_warning(self) -> None:
        """Should show low warning."""
        result = context_monitor.get_context_display({"percent": 80, "warning": "low"})
        assert "LOW!" in result

    def test_contains_progress_bar(self) -> None:
        """Should contain progress bar characters."""
        result = context_monitor.get_context_display({"percent": 50})
        # Should have some filled and some empty segments
        assert "█" in result
        assert "▁" in result


class TestGetDirectoryDisplay:
    """Tests for get_directory_display function."""

    def test_returns_unknown_for_empty_data(self) -> None:
        """Should return 'unknown' when no directory data available."""
        result = context_monitor.get_directory_display({})
        assert result == "unknown"

    def test_returns_basename_for_current_dir_only(self) -> None:
        """Should return basename when only current_dir provided."""
        result = context_monitor.get_directory_display({"current_dir": "/home/user/projects/myapp"})
        assert result == "myapp"

    def test_returns_basename_for_project_dir_only(self) -> None:
        """Should return basename when only project_dir provided."""
        result = context_monitor.get_directory_display({"project_dir": "/home/user/projects/myapp"})
        assert result == "myapp"

    def test_returns_relative_path_when_current_in_project(self) -> None:
        """Should return relative path when current_dir is inside project_dir."""
        result = context_monitor.get_directory_display(
            {
                "current_dir": "/home/user/myapp/src/components",
                "project_dir": "/home/user/myapp",
            }
        )
        assert result == "src/components"

    def test_returns_project_basename_when_same_dir(self) -> None:
        """Should return project basename when current and project dirs are same."""
        result = context_monitor.get_directory_display(
            {
                "current_dir": "/home/user/myapp",
                "project_dir": "/home/user/myapp",
            }
        )
        assert result == "myapp"

    def test_returns_current_basename_when_outside_project(self) -> None:
        """Should return current basename when current_dir is outside project_dir."""
        result = context_monitor.get_directory_display(
            {
                "current_dir": "/home/user/other/place",
                "project_dir": "/home/user/myapp",
            }
        )
        assert result == "place"


class TestGetSessionMetrics:
    """Tests for get_session_metrics function."""

    def test_returns_empty_for_none(self) -> None:
        """Should return empty string for None cost data."""
        result = context_monitor.get_session_metrics(None)
        assert result == ""

    def test_returns_empty_for_empty_data(self) -> None:
        """Should return empty string for empty cost data."""
        result = context_monitor.get_session_metrics({})
        assert result == ""

    def test_formats_small_cost_in_cents(self) -> None:
        """Should format small costs in cents."""
        result = context_monitor.get_session_metrics({"total_cost_usd": 0.005})
        assert "¢" in result
        assert "💰" in result

    def test_formats_larger_cost_in_dollars(self) -> None:
        """Should format larger costs in dollars."""
        result = context_monitor.get_session_metrics({"total_cost_usd": 0.15})
        assert "$" in result
        assert "0.150" in result

    def test_green_color_for_cheap_sessions(self) -> None:
        """Should use green color for cheap sessions."""
        result = context_monitor.get_session_metrics({"total_cost_usd": 0.01})
        # Green ANSI code
        assert "\033[32m" in result

    def test_yellow_color_for_moderate_cost(self) -> None:
        """Should use yellow color for moderate cost."""
        result = context_monitor.get_session_metrics({"total_cost_usd": 0.07})
        # Yellow ANSI code
        assert "\033[33m" in result

    def test_red_color_for_expensive_sessions(self) -> None:
        """Should use red color for expensive sessions."""
        result = context_monitor.get_session_metrics({"total_cost_usd": 0.20})
        # Red ANSI code
        assert "\033[31m" in result

    def test_formats_duration_in_seconds(self) -> None:
        """Should format short durations in seconds."""
        result = context_monitor.get_session_metrics({"total_duration_ms": 30000})
        assert "30s" in result
        assert "⏱" in result

    def test_formats_duration_in_minutes(self) -> None:
        """Should format longer durations in minutes."""
        result = context_monitor.get_session_metrics({"total_duration_ms": 300000})
        assert "5m" in result

    def test_shows_net_lines_added(self) -> None:
        """Should show net lines added."""
        result = context_monitor.get_session_metrics(
            {"total_lines_added": 100, "total_lines_removed": 20}
        )
        assert "+80" in result
        assert "📝" in result

    def test_shows_net_lines_removed(self) -> None:
        """Should show net lines removed."""
        result = context_monitor.get_session_metrics(
            {"total_lines_added": 20, "total_lines_removed": 100}
        )
        assert "-80" in result

    def test_combines_all_metrics(self) -> None:
        """Should combine all metrics when available."""
        result = context_monitor.get_session_metrics(
            {
                "total_cost_usd": 0.05,
                "total_duration_ms": 120000,
                "total_lines_added": 50,
                "total_lines_removed": 10,
            }
        )
        assert "💰" in result
        assert "⏱" in result
        assert "📝" in result
        assert "|" in result  # Separator


class TestMain:
    """Tests for main function."""

    def test_outputs_status_line(self) -> None:
        """Should output a formatted status line."""
        input_data = {
            "model": {"display_name": "Claude Sonnet"},
            "workspace": {"current_dir": "/home/user/myapp"},
            "transcript_path": "",
            "cost": {},
        }

        with (
            patch("sys.stdin", StringIO(json.dumps(input_data))),
            patch("sys.stdout", new_callable=StringIO) as mock_stdout,
        ):
            context_monitor.main()
            output = mock_stdout.getvalue()

        assert "Claude Sonnet" in output
        assert "myapp" in output
        assert "📁" in output
        assert "🧠" in output

    def test_handles_missing_model_gracefully(self) -> None:
        """Should handle missing model data."""
        input_data = {
            "workspace": {"current_dir": "/home/user/myapp"},
            "transcript_path": "",
            "cost": {},
        }

        with (
            patch("sys.stdin", StringIO(json.dumps(input_data))),
            patch("sys.stdout", new_callable=StringIO) as mock_stdout,
        ):
            context_monitor.main()
            output = mock_stdout.getvalue()

        assert "Claude" in output  # Default model name

    def test_error_fallback_on_exception(self) -> None:
        """Should show fallback display on error."""
        with (
            patch("sys.stdin", StringIO("invalid json")),
            patch("sys.stdout", new_callable=StringIO) as mock_stdout,
        ):
            context_monitor.main()
            output = mock_stdout.getvalue()

        assert "[Claude]" in output
        assert "Error" in output

    def test_includes_context_from_transcript(self, tmp_path: Path) -> None:
        """Should include context info when transcript has usage data."""
        transcript = tmp_path / "transcript.jsonl"
        transcript_entry = {
            "type": "assistant",
            "message": {
                "usage": {
                    "input_tokens": 100000,
                    "cache_read_input_tokens": 0,
                    "cache_creation_input_tokens": 0,
                }
            },
        }
        transcript.write_text(json.dumps(transcript_entry) + "\n")

        input_data = {
            "model": {"display_name": "Claude"},
            "workspace": {"current_dir": "/home/user/app"},
            "transcript_path": str(transcript),
            "cost": {},
        }

        with (
            patch("sys.stdin", StringIO(json.dumps(input_data))),
            patch("sys.stdout", new_callable=StringIO) as mock_stdout,
        ):
            context_monitor.main()
            output = mock_stdout.getvalue()

        # Should show percentage (100k / 200k = 50%)
        assert "50%" in output

    def test_uses_context_aware_model_coloring(self, tmp_path: Path) -> None:
        """Should color model name based on context usage."""
        transcript = tmp_path / "transcript.jsonl"
        transcript_entry = {
            "type": "assistant",
            "message": {
                "usage": {
                    "input_tokens": 180000,  # 90% usage
                    "cache_read_input_tokens": 0,
                    "cache_creation_input_tokens": 0,
                }
            },
        }
        transcript.write_text(json.dumps(transcript_entry) + "\n")

        input_data = {
            "model": {"display_name": "Claude"},
            "workspace": {},
            "transcript_path": str(transcript),
            "cost": {},
        }

        with (
            patch("sys.stdin", StringIO(json.dumps(input_data))),
            patch("sys.stdout", new_callable=StringIO) as mock_stdout,
        ):
            context_monitor.main()
            output = mock_stdout.getvalue()

        # High usage should use red coloring
        assert "\033[31m" in output
