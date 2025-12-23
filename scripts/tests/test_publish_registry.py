"""Tests for publish_registry.py - Registry publishing to GitHub Gist."""

import os
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from scripts.publish_registry import (
    ERR_CREDENTIALS_NOT_FOUND,
    get_existing_gist_id,
    get_github_token,
)


class TestGetGithubToken:
    """Tests for get_github_token function."""

    def test_returns_credential_from_environment(self) -> None:
        """Test that credential is retrieved from GITHUB_TOKEN environment variable."""
        test_value = "test-credential-123"
        with patch.dict(os.environ, {"GITHUB_TOKEN": test_value}):
            result = get_github_token()
            assert result == test_value

    def test_returns_credential_from_git_config(self) -> None:
        """Test that credential is retrieved from git config when env var not set."""
        with patch.dict(os.environ, {}, clear=True):
            # Remove GITHUB_TOKEN if it exists
            os.environ.pop("GITHUB_TOKEN", None)

            mock_result = MagicMock()
            mock_result.returncode = 0
            mock_result.stdout = "git-config-credential\n"

            with patch("subprocess.run", return_value=mock_result) as mock_run:
                result = get_github_token()

                assert result == "git-config-credential"
                mock_run.assert_called_once()
                call_args = mock_run.call_args[0][0]
                assert "git" in call_args
                assert "config" in call_args

    def test_raises_when_no_credential_found(self) -> None:
        """Test that RuntimeError is raised when no credential is available."""
        with patch.dict(os.environ, {}, clear=True):
            os.environ.pop("GITHUB_TOKEN", None)

            mock_result = MagicMock()
            mock_result.returncode = 1
            mock_result.stdout = ""

            with patch("subprocess.run", return_value=mock_result):
                with pytest.raises(RuntimeError) as exc_info:
                    get_github_token()

                assert ERR_CREDENTIALS_NOT_FOUND in str(exc_info.value)

    def test_env_var_takes_precedence_over_git_config(self) -> None:
        """Test that environment variable is preferred over git config."""
        test_value = "env-credential"
        with (
            patch.dict(os.environ, {"GITHUB_TOKEN": test_value}),
            patch("subprocess.run") as mock_run,
        ):
            # Even if git config would return a credential, env var should be used
            result = get_github_token()

            assert result == test_value
            # subprocess.run should NOT be called when env var exists
            mock_run.assert_not_called()


class TestGetExistingGistId:
    """Tests for get_existing_gist_id function."""

    def test_returns_gist_id_from_url_file(self, tmp_path: Path) -> None:
        """Test extracting gist ID from .gist-registry-url file."""
        url_file = tmp_path / ".gist-registry-url"
        url_file.write_text("https://gist.github.com/user/abc123def456")

        gist_id = get_existing_gist_id(tmp_path)

        assert gist_id == "abc123def456"

    def test_returns_none_when_file_not_exists(self, tmp_path: Path) -> None:
        """Test returns None when .gist-registry-url doesn't exist."""
        gist_id = get_existing_gist_id(tmp_path)

        assert gist_id is None

    def test_handles_url_with_trailing_slash(self, tmp_path: Path) -> None:
        """Test handling URLs with trailing slashes."""
        url_file = tmp_path / ".gist-registry-url"
        url_file.write_text("https://gist.github.com/user/gist123/")

        gist_id = get_existing_gist_id(tmp_path)

        assert gist_id == "gist123"

    def test_handles_url_with_whitespace(self, tmp_path: Path) -> None:
        """Test handling URLs with surrounding whitespace."""
        url_file = tmp_path / ".gist-registry-url"
        url_file.write_text("  https://gist.github.com/user/gistid  \n")

        gist_id = get_existing_gist_id(tmp_path)

        assert gist_id == "gistid"

    def test_handles_short_gist_url_format(self, tmp_path: Path) -> None:
        """Test handling short gist URL format (without username)."""
        url_file = tmp_path / ".gist-registry-url"
        url_file.write_text("https://gist.github.com/shortid")

        gist_id = get_existing_gist_id(tmp_path)

        assert gist_id == "shortid"
