"""Tests for history_archival.py - history.jsonl archival script."""

import gzip
import json
import logging
import sys
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest


# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from history_archival import (
    archive_history,
    format_size,
    get_archive_dir,
    get_claude_dir,
    get_history_file,
    main,
    parse_timestamp,
    print_summary,
    process_entry,
    write_archives,
)


class TestPathFunctions:
    """Tests for path utility functions."""

    def test_get_claude_dir(self) -> None:
        """Should return ~/.claude path."""
        result = get_claude_dir()
        assert result == Path.home() / ".claude"

    def test_get_history_file(self) -> None:
        """Should return ~/.claude/history.jsonl path."""
        result = get_history_file()
        assert result == Path.home() / ".claude" / "history.jsonl"

    def test_get_archive_dir(self) -> None:
        """Should return ~/.claude/archive/history path."""
        result = get_archive_dir()
        assert result == Path.home() / ".claude" / "archive" / "history"


class TestFormatSize:
    """Tests for format_size function."""

    def test_bytes(self) -> None:
        """Small sizes should display in bytes."""
        assert format_size(500) == "500.0 B"

    def test_kilobytes(self) -> None:
        """Sizes around 1KB should display in KB."""
        assert format_size(1024) == "1.0 KB"

    def test_megabytes(self) -> None:
        """Sizes around 1MB should display in MB."""
        assert format_size(1024 * 1024) == "1.0 MB"

    def test_gigabytes(self) -> None:
        """Sizes around 1GB should display in GB."""
        assert format_size(1024 * 1024 * 1024) == "1.0 GB"

    def test_terabytes(self) -> None:
        """Very large sizes should display in TB."""
        assert format_size(1024 * 1024 * 1024 * 1024) == "1.0 TB"


class TestParseTimestamp:
    """Tests for parse_timestamp function."""

    def test_unix_timestamp_seconds(self) -> None:
        """Should parse Unix timestamp in seconds."""
        ts = datetime(2024, 1, 15, 12, 0, 0).timestamp()
        result = parse_timestamp({"timestamp": ts})
        assert result is not None
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15

    def test_unix_timestamp_milliseconds(self) -> None:
        """Should parse Unix timestamp in milliseconds."""
        ts = datetime(2024, 1, 15, 12, 0, 0).timestamp() * 1000
        result = parse_timestamp({"timestamp": ts})
        assert result is not None
        assert result.year == 2024
        assert result.month == 1
        assert result.day == 15

    def test_missing_timestamp(self) -> None:
        """Should return None for missing timestamp."""
        result = parse_timestamp({})
        assert result is None

    def test_none_timestamp(self) -> None:
        """Should return None for None timestamp."""
        result = parse_timestamp({"timestamp": None})
        assert result is None

    def test_invalid_timestamp(self) -> None:
        """Should return None for invalid timestamp values."""
        result = parse_timestamp({"timestamp": -99999999999999})
        assert result is None


class TestProcessEntry:
    """Tests for process_entry function."""

    def test_valid_recent_entry(self) -> None:
        """Recent entries should be kept."""
        now = datetime.now()
        entry = {"timestamp": now.timestamp(), "data": "test"}
        line = json.dumps(entry)
        recent: list[str] = []
        archives: dict[str, list[str]] = {}
        stats = {"total_entries": 0, "kept_entries": 0, "archived_entries": 0, "parse_errors": 0}
        cutoff = now - timedelta(days=30)

        process_entry(line, cutoff, recent, archives, stats, verbose=False)

        assert len(recent) == 1
        assert stats["kept_entries"] == 1
        assert stats["archived_entries"] == 0

    def test_valid_old_entry(self) -> None:
        """Old entries should be archived."""

        old_date = datetime.now() - timedelta(days=60)
        entry = {"timestamp": old_date.timestamp(), "data": "test"}
        line = json.dumps(entry)
        recent: list[str] = []
        archives: dict[str, list[str]] = defaultdict(list)
        stats = {"total_entries": 0, "kept_entries": 0, "archived_entries": 0, "parse_errors": 0}
        cutoff = datetime.now() - timedelta(days=30)

        process_entry(line, cutoff, recent, archives, stats, verbose=False)

        assert len(recent) == 0
        assert stats["archived_entries"] == 1
        month_key = old_date.strftime("%Y-%m")
        assert month_key in archives

    def test_invalid_json(self) -> None:
        """Invalid JSON should be kept with parse error."""
        line = "not valid json"
        recent: list[str] = []
        archives: dict[str, list[str]] = {}
        stats = {"total_entries": 0, "kept_entries": 0, "archived_entries": 0, "parse_errors": 0}
        cutoff = datetime.now() - timedelta(days=30)

        process_entry(line, cutoff, recent, archives, stats, verbose=False)

        assert len(recent) == 1
        assert stats["kept_entries"] == 1
        assert stats["parse_errors"] == 1

    def test_missing_timestamp_entry(self) -> None:
        """Entries without timestamp should be kept with parse error."""
        entry = {"data": "test"}
        line = json.dumps(entry)
        recent: list[str] = []
        archives: dict[str, list[str]] = {}
        stats = {"total_entries": 0, "kept_entries": 0, "archived_entries": 0, "parse_errors": 0}
        cutoff = datetime.now() - timedelta(days=30)

        process_entry(line, cutoff, recent, archives, stats, verbose=False)

        assert len(recent) == 1
        assert stats["parse_errors"] == 1


class TestWriteArchives:
    """Tests for write_archives function."""

    def test_empty_archives(self, tmp_path: Path) -> None:
        """Should handle empty archives gracefully."""
        result = write_archives(tmp_path, {}, dry_run=False, verbose=False)
        assert result == []

    def test_creates_archive_file(self, tmp_path: Path) -> None:
        """Should create gzipped archive files."""
        entries = {"2024-01": ['{"timestamp": 1704067200, "data": "test"}']}
        result = write_archives(tmp_path, entries, dry_run=False, verbose=False)

        assert len(result) == 1
        assert "2024-01" in result[0]
        archive_file = tmp_path / "history-2024-01.jsonl.gz"
        assert archive_file.exists()

    def test_archive_content_is_gzipped(self, tmp_path: Path) -> None:
        """Archive files should be properly gzipped."""
        entry_line = '{"timestamp": 1704067200, "data": "test"}'
        entries = {"2024-01": [entry_line]}
        write_archives(tmp_path, entries, dry_run=False, verbose=False)

        archive_file = tmp_path / "history-2024-01.jsonl.gz"
        with gzip.open(archive_file, "rt") as f:
            content = f.read()
            assert entry_line in content

    def test_dry_run_doesnt_create_files(self, tmp_path: Path) -> None:
        """Dry run should not create archive files."""
        entries = {"2024-01": ['{"timestamp": 1704067200, "data": "test"}']}
        result = write_archives(tmp_path, entries, dry_run=True, verbose=False)

        assert len(result) == 1
        archive_file = tmp_path / "history-2024-01.jsonl.gz"
        assert not archive_file.exists()

    def test_appends_to_existing_archive(self, tmp_path: Path) -> None:
        """Should append to existing archive files."""
        archive_file = tmp_path / "history-2024-01.jsonl.gz"
        existing_entry = '{"timestamp": 1704067200, "data": "existing"}'
        with gzip.open(archive_file, "wt") as f:
            f.write(existing_entry + "\n")

        new_entry = '{"timestamp": 1704153600, "data": "new"}'
        entries = {"2024-01": [new_entry]}
        write_archives(tmp_path, entries, dry_run=False, verbose=False)

        with gzip.open(archive_file, "rt") as f:
            content = f.read()
            assert existing_entry in content
            assert new_entry in content

    def test_creates_archive_directory(self, tmp_path: Path) -> None:
        """Should create archive directory if it doesn't exist."""
        archive_dir = tmp_path / "nested" / "archive"
        entries = {"2024-01": ['{"timestamp": 1704067200, "data": "test"}']}
        write_archives(archive_dir, entries, dry_run=False, verbose=False)

        assert archive_dir.exists()

    def test_multiple_months(self, tmp_path: Path) -> None:
        """Should create separate files for different months."""
        entries = {
            "2024-01": ['{"timestamp": 1704067200, "data": "jan"}'],
            "2024-02": ['{"timestamp": 1706745600, "data": "feb"}'],
        }
        result = write_archives(tmp_path, entries, dry_run=False, verbose=False)

        assert len(result) == 2
        assert (tmp_path / "history-2024-01.jsonl.gz").exists()
        assert (tmp_path / "history-2024-02.jsonl.gz").exists()


class TestArchiveHistory:
    """Tests for archive_history function."""

    def test_missing_history_file(self, tmp_path: Path) -> None:
        """Should return error when history file doesn't exist."""
        with patch("history_archival.get_history_file", return_value=tmp_path / "missing.jsonl"):
            result = archive_history()
            assert "error" in result
            assert result["error"] == "History file not found"

    def test_empty_history_file(self, tmp_path: Path) -> None:
        """Should handle empty history file."""
        history_file = tmp_path / "history.jsonl"
        history_file.write_text("")

        with (
            patch("history_archival.get_history_file", return_value=history_file),
            patch("history_archival.get_archive_dir", return_value=tmp_path / "archive"),
        ):
            result = archive_history()
            assert result["total_entries"] == 0
            assert result["kept_entries"] == 0
            assert result["archived_entries"] == 0

    def test_keeps_recent_entries(self, tmp_path: Path) -> None:
        """Should keep entries newer than retention period."""
        history_file = tmp_path / "history.jsonl"
        now = datetime.now()
        entries = [
            json.dumps({"timestamp": now.timestamp(), "data": "entry1"}),
            json.dumps({"timestamp": (now - timedelta(days=5)).timestamp(), "data": "entry2"}),
        ]
        history_file.write_text("\n".join(entries) + "\n")

        with (
            patch("history_archival.get_history_file", return_value=history_file),
            patch("history_archival.get_archive_dir", return_value=tmp_path / "archive"),
        ):
            result = archive_history(retention_days=30)
            assert result["kept_entries"] == 2
            assert result["archived_entries"] == 0

    def test_archives_old_entries(self, tmp_path: Path) -> None:
        """Should archive entries older than retention period."""
        history_file = tmp_path / "history.jsonl"
        old_date = datetime.now() - timedelta(days=60)
        entries = [
            json.dumps({"timestamp": old_date.timestamp(), "data": "old_entry"}),
        ]
        history_file.write_text("\n".join(entries) + "\n")

        with (
            patch("history_archival.get_history_file", return_value=history_file),
            patch("history_archival.get_archive_dir", return_value=tmp_path / "archive"),
        ):
            result = archive_history(retention_days=30)
            assert result["archived_entries"] == 1
            assert len(result["archives_created"]) == 1

    def test_dry_run_doesnt_modify_files(self, tmp_path: Path) -> None:
        """Dry run should not modify history file or create archives."""
        history_file = tmp_path / "history.jsonl"
        old_date = datetime.now() - timedelta(days=60)
        original_content = json.dumps({"timestamp": old_date.timestamp(), "data": "old"}) + "\n"
        history_file.write_text(original_content)
        archive_dir = tmp_path / "archive"

        with (
            patch("history_archival.get_history_file", return_value=history_file),
            patch("history_archival.get_archive_dir", return_value=archive_dir),
        ):
            result = archive_history(retention_days=30, dry_run=True)
            assert result["archived_entries"] == 1
            assert history_file.read_text() == original_content
            assert not archive_dir.exists()

    def test_calculates_sizes(self, tmp_path: Path) -> None:
        """Should calculate size statistics."""
        history_file = tmp_path / "history.jsonl"
        now = datetime.now()
        entry = json.dumps({"timestamp": now.timestamp(), "data": "x" * 100})
        history_file.write_text(entry + "\n")

        with (
            patch("history_archival.get_history_file", return_value=history_file),
            patch("history_archival.get_archive_dir", return_value=tmp_path / "archive"),
        ):
            result = archive_history()
            assert "original_size" in result
            assert "new_size" in result
            assert "space_saved" in result
            assert "original_size_formatted" in result

    def test_custom_retention_days(self, tmp_path: Path) -> None:
        """Should respect custom retention_days parameter."""
        history_file = tmp_path / "history.jsonl"
        # Entry 10 days old
        entry_date = datetime.now() - timedelta(days=10)
        entry = json.dumps({"timestamp": entry_date.timestamp(), "data": "test"})
        history_file.write_text(entry + "\n")

        with (
            patch("history_archival.get_history_file", return_value=history_file),
            patch("history_archival.get_archive_dir", return_value=tmp_path / "archive"),
        ):
            # With 30 day retention, entry should be kept
            result = archive_history(retention_days=30)
            assert result["kept_entries"] == 1
            assert result["archived_entries"] == 0


class TestPrintSummary:
    """Tests for print_summary function."""

    def test_logs_summary_info(self, caplog: pytest.LogCaptureFixture) -> None:
        """Should log summary information."""
        stats = {
            "total_entries": 100,
            "kept_entries": 80,
            "archived_entries": 20,
            "original_size_formatted": "10.0 KB",
            "new_size_formatted": "8.0 KB",
            "space_saved_formatted": "2.0 KB",
            "parse_errors": 0,
            "archives_created": ["2024-01 (20 entries)"],
        }

        with caplog.at_level(logging.INFO):
            print_summary(stats, dry_run=False)
            assert "Total entries processed: 100" in caplog.text
            assert "Entries kept" in caplog.text
            assert "Entries archived: 20" in caplog.text

    def test_logs_dry_run_notice(self, caplog: pytest.LogCaptureFixture) -> None:
        """Should indicate dry run in output."""
        stats = {
            "total_entries": 0,
            "kept_entries": 0,
            "archived_entries": 0,
            "original_size_formatted": "0.0 B",
            "new_size_formatted": "0.0 B",
            "space_saved_formatted": "0.0 B",
        }

        with caplog.at_level(logging.INFO):
            print_summary(stats, dry_run=True)
            assert "DRY RUN" in caplog.text

    def test_logs_parse_errors(self, caplog: pytest.LogCaptureFixture) -> None:
        """Should warn about parse errors."""
        stats = {
            "total_entries": 10,
            "kept_entries": 10,
            "archived_entries": 0,
            "original_size_formatted": "1.0 KB",
            "new_size_formatted": "1.0 KB",
            "space_saved_formatted": "0.0 B",
            "parse_errors": 3,
        }

        with caplog.at_level(logging.WARNING):
            print_summary(stats, dry_run=False)
            assert "parse errors" in caplog.text.lower()


class TestMain:
    """Tests for main function."""

    def test_main_success(self, tmp_path: Path) -> None:
        """Main should return 0 on success."""
        history_file = tmp_path / "history.jsonl"
        history_file.write_text("")

        with (
            patch("history_archival.get_history_file", return_value=history_file),
            patch("history_archival.get_archive_dir", return_value=tmp_path / "archive"),
            patch("sys.argv", ["history_archival.py"]),
        ):
            result = main()
            assert result == 0

    def test_main_with_dry_run(self, tmp_path: Path) -> None:
        """Main should handle --dry-run argument."""
        history_file = tmp_path / "history.jsonl"
        history_file.write_text("")

        with (
            patch("history_archival.get_history_file", return_value=history_file),
            patch("history_archival.get_archive_dir", return_value=tmp_path / "archive"),
            patch("sys.argv", ["history_archival.py", "--dry-run"]),
        ):
            result = main()
            assert result == 0

    def test_main_with_custom_days(self, tmp_path: Path) -> None:
        """Main should handle --days argument."""
        history_file = tmp_path / "history.jsonl"
        history_file.write_text("")

        with (
            patch("history_archival.get_history_file", return_value=history_file),
            patch("history_archival.get_archive_dir", return_value=tmp_path / "archive"),
            patch("sys.argv", ["history_archival.py", "--days", "60"]),
        ):
            result = main()
            assert result == 0

    def test_main_with_verbose(self, tmp_path: Path) -> None:
        """Main should handle --verbose argument."""
        history_file = tmp_path / "history.jsonl"
        history_file.write_text("")

        with (
            patch("history_archival.get_history_file", return_value=history_file),
            patch("history_archival.get_archive_dir", return_value=tmp_path / "archive"),
            patch("sys.argv", ["history_archival.py", "--verbose"]),
        ):
            result = main()
            assert result == 0

    def test_main_returns_error_on_missing_file(self) -> None:
        """Main should return 1 when history file doesn't exist."""
        with (
            patch(
                "history_archival.get_history_file",
                return_value=Path("/nonexistent/history.jsonl"),
            ),
            patch("sys.argv", ["history_archival.py"]),
        ):
            result = main()
            assert result == 1
