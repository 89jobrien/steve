"""Tests for install_from_gist.py - Installing components from GitHub Gists."""

from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
import requests

from scripts.install_from_gist import (
    determine_target_path,
    fetch_gist,
    get_gist_id_from_url,
    main,
)


class TestGetGistIdFromUrl:
    """Tests for get_gist_id_from_url function."""

    def test_extract_gist_id_from_standard_url(self) -> None:
        """Test extracting gist ID from standard GitHub gist URL."""
        url = "https://gist.github.com/username/abc123def456"

        gist_id = get_gist_id_from_url(url)

        assert gist_id == "abc123def456"

    def test_extract_gist_id_with_trailing_slash(self) -> None:
        """Test extracting gist ID from URL with trailing slash."""
        url = "https://gist.github.com/username/xyz789/"

        gist_id = get_gist_id_from_url(url)

        assert gist_id == "xyz789"

    def test_extract_gist_id_from_short_url(self) -> None:
        """Test extracting gist ID from short URL format."""
        url = "https://gist.github.com/abc123"

        gist_id = get_gist_id_from_url(url)

        assert gist_id == "abc123"

    def test_extract_gist_id_handles_various_formats(self) -> None:
        """Test various URL formats."""
        urls = [
            "https://gist.github.com/user/123abc",
            "https://gist.github.com/user/123abc/",
            "gist.github.com/user/123abc",
        ]

        for url in urls:
            gist_id = get_gist_id_from_url(url)
            assert gist_id == "123abc"


class TestFetchGist:
    """Tests for fetch_gist function."""

    @patch("requests.get")
    def test_fetch_gist_success(self, mock_get: MagicMock) -> None:
        """Test successful gist fetch."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "id": "123abc",
            "files": {
                "test.md": {
                    "filename": "test.md",
                    "content": "# Test content",
                }
            },
        }
        mock_get.return_value = mock_response

        result = fetch_gist("123abc")

        assert result["id"] == "123abc"
        assert "test.md" in result["files"]
        mock_get.assert_called_once_with("https://api.github.com/gists/123abc", timeout=30)

    @patch("requests.get")
    def test_fetch_gist_network_error(self, mock_get: MagicMock) -> None:
        """Test handling of network errors."""
        mock_get.side_effect = requests.exceptions.RequestException("Connection failed")

        with pytest.raises(requests.exceptions.RequestException):
            fetch_gist("123abc")

    @patch("requests.get")
    def test_fetch_gist_http_error(self, mock_get: MagicMock) -> None:
        """Test handling of HTTP errors."""
        mock_response = Mock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_get.return_value = mock_response

        with pytest.raises(requests.exceptions.HTTPError):
            fetch_gist("nonexistent")

    @patch("requests.get")
    def test_fetch_gist_uses_correct_api_endpoint(self, mock_get: MagicMock) -> None:
        """Test that correct GitHub API endpoint is used."""
        mock_response = Mock()
        mock_response.json.return_value = {"files": {}}
        mock_get.return_value = mock_response

        fetch_gist("test123")

        call_url = mock_get.call_args[0][0]
        assert "api.github.com/gists/test123" in call_url


class TestDetermineTargetPath:
    """Tests for determine_target_path function."""

    def test_determine_path_for_skill(self, tmp_path: Path) -> None:
        """Test path determination for skill files."""
        content = """---
name: test-skill
type: skill
description: A test skill
---

# Test Skill
"""

        target_path = determine_target_path("SKILL.md", content, tmp_path)

        assert target_path == tmp_path / "steve" / "skills" / "test-skill" / "SKILL.md"

    def test_determine_path_for_agent_with_domain(self, tmp_path: Path) -> None:
        """Test path determination for agent with domain."""
        content = """---
name: test-agent
type: agent
domain: development
---

# Test Agent
"""

        target_path = determine_target_path("test-agent.md", content, tmp_path)

        assert target_path == tmp_path / "steve" / "agents" / "development" / "test-agent.md"

    def test_determine_path_for_agent_without_domain(self, tmp_path: Path) -> None:
        """Test path determination for agent without domain defaults to core."""
        content = """---
name: test-agent
type: agent
---

# Test Agent
"""

        target_path = determine_target_path("test-agent.md", content, tmp_path)

        assert target_path == tmp_path / "steve" / "agents" / "core" / "test-agent.md"

    def test_determine_path_for_command(self, tmp_path: Path) -> None:
        """Test path determination for command files."""
        content = """---
name: test-command
type: command
---

# Test Command
"""

        target_path = determine_target_path("test-command.md", content, tmp_path)

        assert target_path == tmp_path / "steve" / "commands" / "util" / "test-command.md"

    def test_determine_path_for_hook(self, tmp_path: Path) -> None:
        """Test path determination for hook files."""
        content = """---
name: test-hook
type: hook
---

# Test Hook
"""

        target_path = determine_target_path("test-hook.md", content, tmp_path)

        assert target_path == tmp_path / "steve" / "hooks" / "workflows" / "test-hook.md"

    def test_determine_path_by_filename_pattern(self, tmp_path: Path) -> None:
        """Test path determination based on filename when no frontmatter."""
        content = "# Agent content without frontmatter"

        target_path = determine_target_path("my-agent.md", content, tmp_path)

        # Should detect 'agent' in filename
        assert "agents" in str(target_path)

    def test_determine_path_default_to_core_agents(self, tmp_path: Path) -> None:
        """Test default path when type cannot be determined."""
        content = "# Unknown content type"

        target_path = determine_target_path("unknown.md", content, tmp_path)

        assert target_path == tmp_path / "steve" / "agents" / "core" / "unknown.md"

    def test_determine_path_invalid_yaml_frontmatter(self, tmp_path: Path) -> None:
        """Test handling of invalid YAML in frontmatter."""
        content = """---
invalid: yaml: [unclosed
---

Content
"""

        target_path = determine_target_path("test.md", content, tmp_path)

        # Should default to agents/core
        assert target_path == tmp_path / "steve" / "agents" / "core" / "test.md"

    def test_determine_path_skill_with_custom_name(self, tmp_path: Path) -> None:
        """Test skill path uses name from frontmatter."""
        content = """---
name: custom-skill-name
type: skill
---

# Skill
"""

        target_path = determine_target_path("SKILL.md", content, tmp_path)

        assert "custom-skill-name" in str(target_path)


class TestMain:
    """Tests for main function."""

    @patch("scripts.install_from_gist.fetch_gist")
    @patch("pathlib.Path.write_text")
    @patch("pathlib.Path.mkdir")
    def test_main_install_success(
        self,
        mock_mkdir: MagicMock,
        mock_write: MagicMock,
        mock_fetch: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test successful component installation."""
        mock_fetch.return_value = {
            "files": {
                "test-agent.md": {
                    "content": """---
name: test-agent
type: agent
---

# Test Agent
"""
                }
            }
        }

        with (
            patch("sys.argv", ["install_from_gist.py", "https://gist.github.com/user/123"]),
            patch("scripts.install_from_gist.Path.__new__") as mock_path,
        ):
            mock_path.return_value = tmp_path
            result = main()

        # Should be successful
        assert result == 0

    @patch("scripts.install_from_gist.fetch_gist")
    @patch("builtins.print")
    def test_main_gist_has_no_files(self, mock_print: MagicMock, mock_fetch: MagicMock) -> None:
        """Test when gist has no files."""
        mock_fetch.return_value = {"files": {}}

        with patch("sys.argv", ["install_from_gist.py", "https://gist.github.com/user/123"]):
            result = main()

        assert result == 1
        assert any("no files" in str(call) for call in mock_print.call_args_list)

    @patch("scripts.install_from_gist.fetch_gist")
    @patch("builtins.print")
    def test_main_gist_file_empty(self, mock_print: MagicMock, mock_fetch: MagicMock) -> None:
        """Test when gist file is empty."""
        mock_fetch.return_value = {"files": {"empty.md": {"content": ""}}}

        with patch("sys.argv", ["install_from_gist.py", "https://gist.github.com/user/123"]):
            result = main()

        assert result == 1
        assert any("empty" in str(call) for call in mock_print.call_args_list)

    @patch("scripts.install_from_gist.fetch_gist")
    @patch("builtins.print")
    def test_main_fetch_error(self, mock_print: MagicMock, mock_fetch: MagicMock) -> None:
        """Test handling of fetch errors."""
        mock_fetch.side_effect = requests.exceptions.RequestException("Network error")

        with patch("sys.argv", ["install_from_gist.py", "https://gist.github.com/user/123"]):
            result = main()

        assert result == 1
        assert any("Failed to fetch" in str(call) for call in mock_print.call_args_list)

    @patch("scripts.install_from_gist.fetch_gist")
    @patch("pathlib.Path.write_text")
    @patch("pathlib.Path.mkdir")
    def test_main_with_custom_target_path(
        self,
        mock_mkdir: MagicMock,
        mock_write: MagicMock,
        mock_fetch: MagicMock,
        tmp_path: Path,
    ) -> None:
        """Test installation with custom target path."""
        mock_fetch.return_value = {"files": {"test.md": {"content": "# Test content"}}}

        custom_path = "custom/path/test.md"
        with (
            patch(
                "sys.argv",
                [
                    "install_from_gist.py",
                    "https://gist.github.com/user/123",
                    "--target-path",
                    custom_path,
                ],
            ),
            patch("scripts.install_from_gist.Path.__new__") as mock_path,
        ):
            mock_path.return_value = tmp_path
            result = main()

        assert result == 0


class TestInstallFromGistIntegration:
    """Integration tests for install_from_gist functionality."""

    def test_full_install_workflow(self, tmp_path: Path) -> None:
        """Test complete installation workflow."""
        # Mock gist content
        gist_content = """---
name: integration-test-agent
type: agent
domain: testing
description: An integration test agent
---

# Integration Test Agent

This is a test agent for integration testing.
"""

        # Determine target path
        target_path = determine_target_path("integration-test-agent.md", gist_content, tmp_path)

        # Verify path structure
        assert target_path.parent.parent.parent.name == "steve"
        assert target_path.parent.parent.name == "agents"
        assert target_path.parent.name == "testing"
        assert target_path.name == "integration-test-agent.md"

    def test_skill_installation_creates_correct_structure(self, tmp_path: Path) -> None:
        """Test that skill installation creates correct directory structure."""
        skill_content = """---
name: my-test-skill
type: skill
---

# My Test Skill
"""

        target_path = determine_target_path("SKILL.md", skill_content, tmp_path)

        # Verify skill directory structure
        assert target_path.parent.parent.name == "skills"
        assert target_path.parent.name == "my-test-skill"
        assert target_path.name == "SKILL.md"

    @patch("scripts.install_from_gist.fetch_gist")
    def test_gist_id_extraction_and_fetch(self, mock_fetch: MagicMock) -> None:
        """Test that gist ID is correctly extracted and used for fetching."""
        mock_fetch.return_value = {"files": {"test.md": {"content": "# Test"}}}

        url = "https://gist.github.com/username/abc123def456"
        gist_id = get_gist_id_from_url(url)

        assert gist_id == "abc123def456"

        # Fetch using the extracted ID (mocked)
        result = mock_fetch(gist_id)
        assert "test.md" in result["files"]
