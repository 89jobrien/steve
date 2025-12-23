"""Tests for build_projects_dataset.py - projects dataset builder script."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

from steve.helpers.build_projects_dataset import main


class TestMain:
    """Tests for main function."""

    @patch("steve.helpers.build_projects_dataset.iter_project_files")
    @patch("steve.helpers.build_projects_dataset.iter_dataset_rows")
    def test_creates_output_directory(
        self,
        mock_iter_dataset_rows: MagicMock,
        mock_iter_project_files: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Should create output directory if it doesn't exist."""
        projects_dir = tmp_path / "projects"
        projects_dir.mkdir()
        out_file = tmp_path / "nested" / "output" / "dataset.jsonl"

        mock_iter_project_files.return_value = []
        mock_iter_dataset_rows.return_value = iter([])

        with patch(
            "sys.argv",
            [
                "build_projects_dataset.py",
                "--projects-dir",
                str(projects_dir),
                "--out",
                str(out_file),
            ],
        ):
            result = main()
            assert result == 0
            assert out_file.parent.exists()

    @patch("steve.helpers.build_projects_dataset.iter_project_files")
    @patch("steve.helpers.build_projects_dataset.iter_dataset_rows")
    def test_writes_jsonl_output(
        self,
        mock_iter_dataset_rows: MagicMock,
        mock_iter_project_files: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Should write rows to JSONL file."""
        projects_dir = tmp_path / "projects"
        projects_dir.mkdir()
        out_file = tmp_path / "dataset.jsonl"

        mock_rows = [
            {"session_id": "s1", "tool_name": "Read", "t": 0},
            {"session_id": "s1", "tool_name": "Write", "t": 1},
        ]

        mock_iter_project_files.return_value = []
        mock_iter_dataset_rows.return_value = iter(mock_rows)

        with patch(
            "sys.argv",
            [
                "build_projects_dataset.py",
                "--projects-dir",
                str(projects_dir),
                "--out",
                str(out_file),
            ],
        ):
            result = main()
            assert result == 0
            assert out_file.exists()

            lines = out_file.read_text().strip().split("\n")
            assert len(lines) == 2
            assert json.loads(lines[0])["tool_name"] == "Read"
            assert json.loads(lines[1])["tool_name"] == "Write"

    @patch("steve.helpers.build_projects_dataset.iter_project_files")
    @patch("steve.helpers.build_projects_dataset.iter_dataset_rows")
    def test_writes_stats_file(
        self,
        mock_iter_dataset_rows: MagicMock,
        mock_iter_project_files: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Should write stats JSON file."""
        projects_dir = tmp_path / "projects"
        projects_dir.mkdir()
        out_file = tmp_path / "dataset.jsonl"

        mock_rows = [
            {"session_id": "s1", "tool_name": "Read", "t": 0},
            {"session_id": "s1", "tool_name": "Read", "t": 1},
            {"session_id": "s1", "tool_name": "Write", "t": 2},
        ]

        # Create a mock file for iter_project_files
        mock_file = MagicMock()
        mock_stat = MagicMock()
        mock_stat.st_mtime = 1000
        mock_file.stat.return_value = mock_stat

        mock_iter_project_files.return_value = [mock_file]
        mock_iter_dataset_rows.return_value = iter(mock_rows)

        with patch(
            "sys.argv",
            [
                "build_projects_dataset.py",
                "--projects-dir",
                str(projects_dir),
                "--out",
                str(out_file),
            ],
        ):
            result = main()
            assert result == 0

            stats_file = tmp_path / "dataset.jsonl.stats.json"
            assert stats_file.exists()

            stats = json.loads(stats_file.read_text())
            assert stats["rows"] == 3
            assert stats["files"] == 1
            assert "tool_name_counts" in stats

    @patch("steve.helpers.build_projects_dataset.iter_project_files")
    @patch("steve.helpers.build_projects_dataset.iter_dataset_rows")
    def test_max_files_limit(
        self,
        mock_iter_dataset_rows: MagicMock,
        mock_iter_project_files: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Should respect --max-files argument."""
        projects_dir = tmp_path / "projects"
        projects_dir.mkdir()
        out_file = tmp_path / "dataset.jsonl"

        # Create mock files
        mock_files = []
        for i in range(5):
            mock_file = MagicMock()
            mock_stat = MagicMock()
            mock_stat.st_mtime = 1000 - i
            mock_file.stat.return_value = mock_stat
            mock_files.append(mock_file)

        files_passed_to_iter: list = []

        def capture_files(files, **kwargs):
            files_passed_to_iter.extend(files)
            return iter([])

        mock_iter_project_files.return_value = mock_files
        mock_iter_dataset_rows.side_effect = capture_files

        with patch(
            "sys.argv",
            [
                "build_projects_dataset.py",
                "--projects-dir",
                str(projects_dir),
                "--out",
                str(out_file),
                "--max-files",
                "2",
            ],
        ):
            main()
            assert len(files_passed_to_iter) == 2

    @patch("steve.helpers.build_projects_dataset.iter_project_files")
    @patch("steve.helpers.build_projects_dataset.iter_dataset_rows")
    def test_max_rows_limit(
        self,
        mock_iter_dataset_rows: MagicMock,
        mock_iter_project_files: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Should respect --max-rows argument."""
        projects_dir = tmp_path / "projects"
        projects_dir.mkdir()
        out_file = tmp_path / "dataset.jsonl"

        # Create many rows
        mock_rows = [{"session_id": "s1", "tool_name": "Read", "t": i} for i in range(10)]

        mock_iter_project_files.return_value = []
        mock_iter_dataset_rows.return_value = iter(mock_rows)

        with patch(
            "sys.argv",
            [
                "build_projects_dataset.py",
                "--projects-dir",
                str(projects_dir),
                "--out",
                str(out_file),
                "--max-rows",
                "3",
            ],
        ):
            result = main()
            assert result == 0

            lines = out_file.read_text().strip().split("\n")
            assert len(lines) == 3

    @patch("steve.helpers.build_projects_dataset.iter_project_files")
    @patch("steve.helpers.build_projects_dataset.iter_dataset_rows")
    def test_max_context_messages(
        self,
        mock_iter_dataset_rows: MagicMock,
        mock_iter_project_files: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Should pass --max-context-messages to iter_dataset_rows."""
        projects_dir = tmp_path / "projects"
        projects_dir.mkdir()
        out_file = tmp_path / "dataset.jsonl"

        captured_kwargs: dict = {}

        def capture_kwargs(files, **kwargs):
            captured_kwargs.update(kwargs)
            return iter([])

        mock_iter_project_files.return_value = []
        mock_iter_dataset_rows.side_effect = capture_kwargs

        with patch(
            "sys.argv",
            [
                "build_projects_dataset.py",
                "--projects-dir",
                str(projects_dir),
                "--out",
                str(out_file),
                "--max-context-messages",
                "25",
            ],
        ):
            main()
            assert captured_kwargs.get("max_context_messages") == 25

    @patch("steve.helpers.build_projects_dataset.iter_project_files")
    @patch("steve.helpers.build_projects_dataset.iter_dataset_rows")
    def test_sorts_files_by_mtime_descending(
        self,
        mock_iter_dataset_rows: MagicMock,
        mock_iter_project_files: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Should sort files by modification time (newest first)."""
        projects_dir = tmp_path / "projects"
        projects_dir.mkdir()
        out_file = tmp_path / "dataset.jsonl"

        # Create mock files with different mtimes
        mock_files = []
        for i, mtime in enumerate([100, 300, 200]):
            mock_file = MagicMock()
            mock_file.name = f"file_{i}"
            mock_stat = MagicMock()
            mock_stat.st_mtime = mtime
            mock_file.stat.return_value = mock_stat
            mock_files.append(mock_file)

        files_passed: list = []

        def capture_files(files, **kwargs):
            files_passed.extend(files)
            return iter([])

        mock_iter_project_files.return_value = mock_files
        mock_iter_dataset_rows.side_effect = capture_files

        with patch(
            "sys.argv",
            [
                "build_projects_dataset.py",
                "--projects-dir",
                str(projects_dir),
                "--out",
                str(out_file),
            ],
        ):
            main()

            # Files should be sorted newest first (300, 200, 100)
            mtimes = [f.stat().st_mtime for f in files_passed]
            assert mtimes == [300, 200, 100]

    @patch("steve.helpers.build_projects_dataset.iter_project_files")
    @patch("steve.helpers.build_projects_dataset.iter_dataset_rows")
    def test_handles_empty_tool_name(
        self,
        mock_iter_dataset_rows: MagicMock,
        mock_iter_project_files: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Should handle rows with missing tool_name."""
        projects_dir = tmp_path / "projects"
        projects_dir.mkdir()
        out_file = tmp_path / "dataset.jsonl"

        mock_rows = [
            {"session_id": "s1", "t": 0},  # No tool_name
            {"session_id": "s1", "tool_name": "Read", "t": 1},
        ]

        mock_iter_project_files.return_value = []
        mock_iter_dataset_rows.return_value = iter(mock_rows)

        with patch(
            "sys.argv",
            [
                "build_projects_dataset.py",
                "--projects-dir",
                str(projects_dir),
                "--out",
                str(out_file),
            ],
        ):
            result = main()
            assert result == 0

            stats_file = tmp_path / "dataset.jsonl.stats.json"
            stats = json.loads(stats_file.read_text())
            assert stats["rows"] == 2
            # Empty string key for missing tool_name
            assert "" in stats["tool_name_counts"]

    @patch("steve.helpers.build_projects_dataset.iter_project_files")
    @patch("steve.helpers.build_projects_dataset.iter_dataset_rows")
    def test_tool_name_counts_in_stats(
        self,
        mock_iter_dataset_rows: MagicMock,
        mock_iter_project_files: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Should count tool_name occurrences correctly in stats."""
        projects_dir = tmp_path / "projects"
        projects_dir.mkdir()
        out_file = tmp_path / "dataset.jsonl"

        mock_rows = [
            {"session_id": "s1", "tool_name": "Read", "t": 0},
            {"session_id": "s1", "tool_name": "Read", "t": 1},
            {"session_id": "s1", "tool_name": "Write", "t": 2},
            {"session_id": "s1", "tool_name": "Read", "t": 3},
        ]

        mock_iter_project_files.return_value = []
        mock_iter_dataset_rows.return_value = iter(mock_rows)

        with patch(
            "sys.argv",
            [
                "build_projects_dataset.py",
                "--projects-dir",
                str(projects_dir),
                "--out",
                str(out_file),
            ],
        ):
            result = main()
            assert result == 0

            stats_file = tmp_path / "dataset.jsonl.stats.json"
            stats = json.loads(stats_file.read_text())
            assert stats["tool_name_counts"]["Read"] == 3
            assert stats["tool_name_counts"]["Write"] == 1
