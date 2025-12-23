"""Tests for debug_rotation.py - debug log rotation script."""

import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import pytest


# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from debug_rotation import (
    format_size,
    get_debug_dir,
    get_file_age_days,
    main,
    rotate_debug_logs,
)


class TestGetDebugDir:
    """Tests for get_debug_dir function."""

    def test_returns_path_object(self) -> None:
        """get_debug_dir should return a Path object."""
        result = get_debug_dir()
        assert isinstance(result, Path)

    def test_returns_correct_path(self) -> None:
        """get_debug_dir should return ~/.claude/debug path."""
        result = get_debug_dir()
        expected = Path.home() / ".claude" / "debug"
        assert result == expected


class TestGetFileAgeDays:
    """Tests for get_file_age_days function."""

    def test_recent_file_age(self, tmp_path: Path) -> None:
        """Recently created file should have age close to 0."""
        test_file = tmp_path / "recent.txt"
        test_file.write_text("test")
        age = get_file_age_days(test_file)
        assert age < 0.01  # Less than ~15 minutes

    def test_old_file_age(self, tmp_path: Path) -> None:
        """File with modified mtime should report correct age."""
        test_file = tmp_path / "old.txt"
        test_file.write_text("test")

        # Set modification time to 10 days ago

        old_time = datetime.now() - timedelta(days=10)
        old_timestamp = old_time.timestamp()
        os.utime(test_file, (old_timestamp, old_timestamp))

        age = get_file_age_days(test_file)
        assert 9.9 < age < 10.1  # Approximately 10 days


class TestFormatSize:
    """Tests for format_size function."""

    def test_bytes(self) -> None:
        """Small sizes should display in bytes."""
        assert format_size(500) == "500.0 B"

    def test_kilobytes(self) -> None:
        """Sizes around 1KB should display in KB."""
        assert format_size(1024) == "1.0 KB"
        assert format_size(2048) == "2.0 KB"

    def test_megabytes(self) -> None:
        """Sizes around 1MB should display in MB."""
        assert format_size(1024 * 1024) == "1.0 MB"
        assert format_size(5 * 1024 * 1024) == "5.0 MB"

    def test_gigabytes(self) -> None:
        """Sizes around 1GB should display in GB."""
        assert format_size(1024 * 1024 * 1024) == "1.0 GB"

    def test_terabytes(self) -> None:
        """Very large sizes should display in TB."""
        assert format_size(1024 * 1024 * 1024 * 1024) == "1.0 TB"

    def test_zero(self) -> None:
        """Zero bytes should display correctly."""
        assert format_size(0) == "0.0 B"

    def test_fractional_values(self) -> None:
        """Fractional values should be formatted correctly."""
        assert format_size(1536) == "1.5 KB"  # 1.5 KB


class TestRotateDebugLogs:
    """Tests for rotate_debug_logs function."""

    def test_nonexistent_directory(self) -> None:
        """Should return error when debug directory doesn't exist."""
        with patch(
            "debug_rotation.get_debug_dir",
            return_value=Path("/nonexistent/path"),
        ):
            result = rotate_debug_logs()
            assert "error" in result
            assert result["error"] == "Debug directory not found"

    def test_empty_directory(self, tmp_path: Path) -> None:
        """Should handle empty directory gracefully."""
        with patch("debug_rotation.get_debug_dir", return_value=tmp_path):
            result = rotate_debug_logs()
            assert result["total_files"] == 0
            assert result["kept_files"] == 0
            assert result["deleted_files"] == 0

    def test_keeps_recent_files(self, tmp_path: Path) -> None:
        """Should keep files newer than retention period."""
        # Create recent files
        for i in range(3):
            (tmp_path / f"recent_{i}.txt").write_text(f"content {i}")

        with patch("debug_rotation.get_debug_dir", return_value=tmp_path):
            result = rotate_debug_logs(retention_days=7)
            assert result["total_files"] == 3
            assert result["kept_files"] == 3
            assert result["deleted_files"] == 0

    def test_deletes_old_files(self, tmp_path: Path) -> None:
        """Should delete files older than retention period."""

        # Create old file
        old_file = tmp_path / "old.txt"
        old_file.write_text("old content")
        old_time = datetime.now() - timedelta(days=10)
        os.utime(old_file, (old_time.timestamp(), old_time.timestamp()))

        with patch("debug_rotation.get_debug_dir", return_value=tmp_path):
            result = rotate_debug_logs(retention_days=7)
            assert result["deleted_files"] == 1
            assert not old_file.exists()

    def test_dry_run_doesnt_delete(self, tmp_path: Path) -> None:
        """Dry run should not delete any files."""

        # Create old file
        old_file = tmp_path / "old.txt"
        old_file.write_text("old content")
        old_time = datetime.now() - timedelta(days=10)
        os.utime(old_file, (old_time.timestamp(), old_time.timestamp()))

        with patch("debug_rotation.get_debug_dir", return_value=tmp_path):
            result = rotate_debug_logs(retention_days=7, dry_run=True)
            assert result["deleted_files"] == 1
            assert old_file.exists()  # File should still exist

    def test_only_processes_txt_files(self, tmp_path: Path) -> None:
        """Should only process .txt files."""
        # Create various file types
        (tmp_path / "log.txt").write_text("text log")
        (tmp_path / "data.json").write_text("{}")
        (tmp_path / "script.py").write_text("print('hello')")

        with patch("debug_rotation.get_debug_dir", return_value=tmp_path):
            result = rotate_debug_logs()
            assert result["total_files"] == 1  # Only .txt file

    def test_calculates_sizes_correctly(self, tmp_path: Path) -> None:
        """Should correctly calculate kept and deleted sizes."""

        # Create recent file (1000 bytes)
        recent_file = tmp_path / "recent.txt"
        recent_file.write_text("x" * 1000)

        # Create old file (500 bytes)
        old_file = tmp_path / "old.txt"
        old_file.write_text("y" * 500)
        old_time = datetime.now() - timedelta(days=10)
        os.utime(old_file, (old_time.timestamp(), old_time.timestamp()))

        with patch("debug_rotation.get_debug_dir", return_value=tmp_path):
            result = rotate_debug_logs(retention_days=7)
            assert result["kept_size"] == 1000
            assert result["deleted_size"] == 500

    def test_formats_sizes_in_result(self, tmp_path: Path) -> None:
        """Should include formatted size strings in result."""
        (tmp_path / "test.txt").write_text("content")

        with patch("debug_rotation.get_debug_dir", return_value=tmp_path):
            result = rotate_debug_logs()
            assert "kept_size_formatted" in result
            assert "deleted_size_formatted" in result

    def test_custom_retention_days(self, tmp_path: Path) -> None:
        """Should respect custom retention_days parameter."""

        # Create file 3 days old
        file_3_days = tmp_path / "three_days.txt"
        file_3_days.write_text("content")
        three_days_ago = datetime.now() - timedelta(days=3)
        os.utime(file_3_days, (three_days_ago.timestamp(), three_days_ago.timestamp()))

        with patch("debug_rotation.get_debug_dir", return_value=tmp_path):
            # With 7 day retention, file should be kept
            result = rotate_debug_logs(retention_days=7)
            assert result["kept_files"] == 1
            assert file_3_days.exists()

            # With 2 day retention, file should be deleted
            result = rotate_debug_logs(retention_days=2)
            assert result["deleted_files"] == 1
            assert not file_3_days.exists()

    def test_verbose_mode(self, tmp_path: Path, caplog: pytest.LogCaptureFixture) -> None:
        """Verbose mode should log file operations."""

        # Create old file
        old_file = tmp_path / "old.txt"
        old_file.write_text("old content")
        old_time = datetime.now() - timedelta(days=10)
        os.utime(old_file, (old_time.timestamp(), old_time.timestamp()))

        with (
            patch("debug_rotation.get_debug_dir", return_value=tmp_path),
            caplog.at_level(logging.INFO),
        ):
            rotate_debug_logs(retention_days=7, verbose=True, dry_run=True)
            assert "DELETE" in caplog.text


class TestMain:
    """Tests for main function."""

    def test_main_success(self, tmp_path: Path) -> None:
        """Main should return 0 on success."""
        with (
            patch("debug_rotation.get_debug_dir", return_value=tmp_path),
            patch("sys.argv", ["debug_rotation.py"]),
        ):
            result = main()
            assert result == 0

    def test_main_with_dry_run(self, tmp_path: Path) -> None:
        """Main should handle --dry-run argument."""
        with (
            patch("debug_rotation.get_debug_dir", return_value=tmp_path),
            patch("sys.argv", ["debug_rotation.py", "--dry-run"]),
        ):
            result = main()
            assert result == 0

    def test_main_with_custom_days(self, tmp_path: Path) -> None:
        """Main should handle --days argument."""
        with (
            patch("debug_rotation.get_debug_dir", return_value=tmp_path),
            patch("sys.argv", ["debug_rotation.py", "--days", "14"]),
        ):
            result = main()
            assert result == 0

    def test_main_with_verbose(self, tmp_path: Path) -> None:
        """Main should handle --verbose argument."""
        with (
            patch("debug_rotation.get_debug_dir", return_value=tmp_path),
            patch("sys.argv", ["debug_rotation.py", "--verbose"]),
        ):
            result = main()
            assert result == 0

    def test_main_with_short_verbose(self, tmp_path: Path) -> None:
        """Main should handle -v argument."""
        with (
            patch("debug_rotation.get_debug_dir", return_value=tmp_path),
            patch("sys.argv", ["debug_rotation.py", "-v"]),
        ):
            result = main()
            assert result == 0

    def test_main_returns_error_on_missing_dir(self) -> None:
        """Main should return 1 when debug directory doesn't exist."""
        with (
            patch(
                "debug_rotation.get_debug_dir",
                return_value=Path("/nonexistent/path"),
            ),
            patch("sys.argv", ["debug_rotation.py"]),
        ):
            result = main()
            assert result == 1

    def test_main_combined_arguments(self, tmp_path: Path) -> None:
        """Main should handle multiple arguments together."""
        with (
            patch("debug_rotation.get_debug_dir", return_value=tmp_path),
            patch(
                "sys.argv",
                ["debug_rotation.py", "--dry-run", "--days", "30", "-v"],
            ),
        ):
            result = main()
            assert result == 0
