"""Tests for detect_secrets.py - Secrets detection script."""

import subprocess
from unittest.mock import MagicMock, patch

from scripts.detect_secrets import (
    check_detect_secrets,
    generate_baseline,
    run_command,
    scan_repository,
)


class TestRunCommand:
    """Tests for run_command function."""

    @patch("subprocess.run")
    def test_run_command_success(self, mock_run: MagicMock) -> None:
        """Test running a successful command."""
        mock_run.return_value = MagicMock(
            stdout="output",
            stderr="",
            returncode=0,
        )

        stdout, stderr, code = run_command(["echo", "test"])

        assert stdout == "output"
        assert stderr == ""
        assert code == 0
        mock_run.assert_called_once()

    @patch("subprocess.run")
    def test_run_command_failure(self, mock_run: MagicMock) -> None:
        """Test running a command that fails."""
        mock_run.return_value = MagicMock(
            stdout="",
            stderr="error message",
            returncode=1,
        )

        stdout, stderr, code = run_command(["false"], check=False)

        assert stdout == ""
        assert stderr == "error message"
        assert code == 1

    @patch("subprocess.run")
    def test_run_command_with_exception(self, mock_run: MagicMock) -> None:
        """Test run_command handles CalledProcessError."""

        mock_run.side_effect = subprocess.CalledProcessError(
            returncode=127,
            cmd=["nonexistent"],
            output="",
            stderr="command not found",
        )

        _, _, code = run_command(["nonexistent"], check=False)

        assert code == 127


class TestCheckDetectSecrets:
    """Tests for check_detect_secrets function."""

    @patch("scripts.detect_secrets.run_command")
    @patch("sys.exit")
    def test_detect_secrets_installed(self, mock_exit: MagicMock, mock_run: MagicMock) -> None:
        """Test when detect-secrets is installed."""
        mock_run.return_value = ("detect-secrets 1.0.0", "", 0)

        check_detect_secrets()

        mock_run.assert_called_once_with(["detect-secrets", "--version"], check=False)
        mock_exit.assert_not_called()

    @patch("scripts.detect_secrets.run_command")
    @patch("sys.exit")
    @patch("builtins.print")
    def test_detect_secrets_not_installed(
        self, mock_print: MagicMock, mock_exit: MagicMock, mock_run: MagicMock
    ) -> None:
        """Test when detect-secrets is not installed."""
        mock_run.return_value = ("", "command not found", 127)

        check_detect_secrets()

        mock_exit.assert_called_once_with(1)
        assert mock_print.call_count >= 2  # Error message and install instructions


class TestGenerateBaseline:
    """Tests for generate_baseline function."""

    @patch("scripts.detect_secrets.run_command")
    @patch("builtins.print")
    def test_generate_baseline_success(self, mock_print: MagicMock, mock_run: MagicMock) -> None:
        """Test successful baseline generation."""
        mock_run.return_value = ("", "", 0)

        result = generate_baseline()

        assert result is True
        # Verify command includes required arguments
        call_args = mock_run.call_args[0][0]
        assert "detect-secrets" in call_args
        assert "scan" in call_args
        assert "--baseline" in call_args
        assert any("exclude-files" in str(arg) for arg in call_args)

    @patch("scripts.detect_secrets.run_command")
    @patch("builtins.print")
    def test_generate_baseline_failure(self, mock_print: MagicMock, mock_run: MagicMock) -> None:
        """Test baseline generation failure."""
        mock_run.return_value = ("", "scan failed", 1)

        result = generate_baseline()

        assert result is False
        # Verify error message printed
        assert any("ERROR" in str(call) for call in mock_print.call_args_list)

    @patch("scripts.detect_secrets.run_command")
    def test_generate_baseline_excludes_common_patterns(self, mock_run: MagicMock) -> None:
        """Test that common patterns are excluded from baseline."""
        mock_run.return_value = ("", "", 0)

        generate_baseline()

        call_args = mock_run.call_args[0][0]
        command_str = " ".join(call_args)

        # Verify common patterns are excluded
        assert "*.pyc" in command_str
        assert "__pycache__" in command_str
        assert ".git" in command_str
        assert ".venv" in command_str
        assert "node_modules" in command_str


class TestScanRepository:
    """Tests for scan_repository function."""

    @patch("pathlib.Path.exists")
    @patch("scripts.detect_secrets.run_command")
    @patch("builtins.print")
    def test_scan_repository_no_baseline(
        self, mock_print: MagicMock, mock_run: MagicMock, mock_exists: MagicMock
    ) -> None:
        """Test scanning when baseline file doesn't exist."""
        mock_exists.return_value = False

        result = scan_repository()

        assert result is False
        mock_run.assert_not_called()
        # Verify warning printed
        assert any("WARNING" in str(call) for call in mock_print.call_args_list)

    @patch("pathlib.Path.exists")
    @patch("scripts.detect_secrets.run_command")
    @patch("builtins.print")
    def test_scan_repository_no_secrets_found(
        self, mock_print: MagicMock, mock_run: MagicMock, mock_exists: MagicMock
    ) -> None:
        """Test scanning when no secrets are detected."""
        mock_exists.return_value = True
        mock_run.return_value = ("", "", 0)

        result = scan_repository()

        assert result is True
        # Verify success message printed
        assert any("No new secrets" in str(call) for call in mock_print.call_args_list)

    @patch("pathlib.Path.exists")
    @patch("scripts.detect_secrets.run_command")
    @patch("builtins.print")
    def test_scan_repository_secrets_found(
        self, mock_print: MagicMock, mock_run: MagicMock, mock_exists: MagicMock
    ) -> None:
        """Test scanning when secrets are detected."""
        mock_exists.return_value = True
        mock_run.return_value = ("Found 2 secrets", "", 1)

        result = scan_repository()

        assert result is False
        # Verify warning printed
        assert any("Potential secrets" in str(call) for call in mock_print.call_args_list)

    @patch("pathlib.Path.exists")
    @patch("scripts.detect_secrets.run_command")
    def test_scan_repository_uses_correct_command(
        self, mock_run: MagicMock, mock_exists: MagicMock
    ) -> None:
        """Test that scan uses correct detect-secrets audit command."""
        mock_exists.return_value = True
        mock_run.return_value = ("", "", 0)

        scan_repository()

        call_args = mock_run.call_args[0][0]
        assert "detect-secrets" in call_args
        assert "audit" in call_args
        assert "--baseline" in call_args
        assert ".secrets.baseline" in call_args


class TestDetectSecretsIntegration:
    """Integration tests for detect_secrets functionality."""

    @patch("scripts.detect_secrets.run_command")
    @patch("pathlib.Path.exists")
    def test_full_workflow_baseline_then_scan(
        self, mock_exists: MagicMock, mock_run: MagicMock
    ) -> None:
        """Test full workflow: generate baseline then scan."""
        # First call for baseline generation
        mock_run.side_effect = [
            ("", "", 0),  # generate_baseline success
            ("", "", 0),  # scan_repository success
        ]
        mock_exists.return_value = True

        # Generate baseline
        baseline_result = generate_baseline()
        assert baseline_result is True

        # Scan repository
        scan_result = scan_repository()
        assert scan_result is True

        # Verify both commands were called
        assert mock_run.call_count == 2

    @patch("scripts.detect_secrets.run_command")
    @patch("pathlib.Path.exists")
    def test_scan_fails_when_secrets_detected(
        self, mock_exists: MagicMock, mock_run: MagicMock
    ) -> None:
        """Test that scan returns False when secrets are detected."""
        mock_exists.return_value = True
        mock_run.return_value = ("Secrets found!", "", 1)

        result = scan_repository()

        assert result is False
