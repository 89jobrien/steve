"""Tests for install_component.py - Component installation from registry."""

import json
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest
import requests

from scripts.install_component import (
    find_component,
    load_local_registry,
    load_remote_registry,
    main,
)


class TestLoadLocalRegistry:
    """Tests for load_local_registry function."""

    def test_load_existing_registry(self, tmp_path: Path) -> None:
        """Test loading an existing local registry file."""
        registry_data = {
            "components": {
                "test-agent": {
                    "name": "test-agent",
                    "type": "agent",
                    "gist_url": "https://gist.github.com/test/123",
                }
            }
        }

        registry_file = tmp_path / ".gist-registry.json"
        registry_file.write_text(json.dumps(registry_data))

        result = load_local_registry(tmp_path)

        assert result == registry_data
        assert "test-agent" in result["components"]

    def test_load_nonexistent_registry(self, tmp_path: Path) -> None:
        """Test loading when registry file doesn't exist."""
        result = load_local_registry(tmp_path)

        assert result == {"components": {}}

    def test_load_empty_registry(self, tmp_path: Path) -> None:
        """Test loading an empty registry file."""
        registry_file = tmp_path / ".gist-registry.json"
        registry_file.write_text("{}")

        result = load_local_registry(tmp_path)

        assert "components" not in result or result["components"] == {}


class TestLoadRemoteRegistry:
    """Tests for load_remote_registry function."""

    @patch("requests.get")
    def test_load_remote_registry_success(self, mock_get: MagicMock) -> None:
        """Test successful loading of remote registry."""
        registry_data = {
            "components": {
                "remote-agent": {
                    "name": "remote-agent",
                    "type": "agent",
                }
            }
        }

        mock_response = Mock()
        mock_response.json.return_value = {
            "files": {
                "registry.json": {
                    "content": json.dumps(registry_data),
                }
            }
        }
        mock_get.return_value = mock_response

        result = load_remote_registry("https://gist.github.com/user/abc123")

        assert result == registry_data
        mock_get.assert_called_once()
        assert "gists/abc123" in mock_get.call_args[0][0]

    @patch("requests.get")
    def test_load_remote_registry_extracts_gist_id(self, mock_get: MagicMock) -> None:
        """Test that gist ID is correctly extracted from URL."""
        mock_response = Mock()
        mock_response.json.return_value = {"files": {"registry.json": {"content": "{}"}}}
        mock_get.return_value = mock_response

        load_remote_registry("https://gist.github.com/user/xyz789/")

        assert "gists/xyz789" in mock_get.call_args[0][0]

    @patch("requests.get")
    def test_load_remote_registry_request_error(self, mock_get: MagicMock) -> None:
        """Test handling of request errors."""
        mock_get.side_effect = requests.exceptions.RequestException("Network error")

        with pytest.raises(requests.exceptions.RequestException):
            load_remote_registry("https://gist.github.com/user/123")

    @patch("requests.get")
    def test_load_remote_registry_no_json_files(self, mock_get: MagicMock) -> None:
        """Test loading when gist has no JSON files."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "files": {
                "README.md": {"content": "# Readme"},
            }
        }
        mock_get.return_value = mock_response

        result = load_remote_registry("https://gist.github.com/user/123")

        assert result == {"components": {}}


class TestFindComponent:
    """Tests for find_component function."""

    def test_find_component_by_exact_name(self) -> None:
        """Test finding component by exact name match."""
        components = {
            "path/to/test-agent.md": {
                "name": "test-agent",
                "type": "agent",
                "domain": "core",
            }
        }

        result = find_component(components, "test-agent")

        assert result is not None
        assert result["name"] == "test-agent"

    def test_find_component_case_insensitive(self) -> None:
        """Test that name matching is case insensitive."""
        components = {
            "path/to/TestAgent.md": {
                "name": "TestAgent",
                "type": "agent",
            }
        }

        result = find_component(components, "testagent")

        assert result is not None
        assert result["name"] == "TestAgent"

    def test_find_component_not_found(self) -> None:
        """Test when component is not found."""
        components = {
            "path/to/other-agent.md": {
                "name": "other-agent",
                "type": "agent",
            }
        }

        result = find_component(components, "nonexistent")

        assert result is None

    def test_find_component_with_type_filter(self) -> None:
        """Test filtering by component type."""
        components = {
            "agent.md": {"name": "test", "type": "agent"},
            "command.md": {"name": "test", "type": "command"},
        }

        result = find_component(components, "test", component_type="command")

        assert result is not None
        assert result["type"] == "command"

    def test_find_component_with_domain_filter(self) -> None:
        """Test filtering by domain."""
        components = {
            "core.md": {"name": "test", "type": "agent", "domain": "core"},
            "dev.md": {"name": "test", "type": "agent", "domain": "development"},
        }

        result = find_component(components, "test", domain="development")

        assert result is not None
        assert result["domain"] == "development"

    @patch("builtins.print")
    def test_find_component_multiple_matches(self, mock_print: MagicMock) -> None:
        """Test when multiple components match the name."""
        components = {
            "agent1.md": {"name": "test", "type": "agent", "domain": "core"},
            "agent2.md": {"name": "test", "type": "agent", "domain": "development"},
        }

        result = find_component(components, "test")

        assert result is None
        assert mock_print.call_count >= 1
        assert any("Multiple components" in str(call) for call in mock_print.call_args_list)

    def test_find_component_multiple_matches_narrowed_by_type(self) -> None:
        """Test that type filter can narrow down multiple matches."""
        components = {
            "agent.md": {"name": "test", "type": "agent"},
            "command.md": {"name": "test", "type": "command"},
        }

        result = find_component(components, "test", component_type="agent")

        assert result is not None
        assert result["type"] == "agent"


class TestMain:
    """Tests for main function."""

    @patch("subprocess.run")
    @patch("scripts.install_component.load_local_registry")
    def test_main_install_success(self, mock_load: MagicMock, mock_subprocess: MagicMock) -> None:
        """Test successful component installation."""
        mock_load.return_value = {
            "components": {
                "test-agent": {
                    "name": "test-agent",
                    "type": "agent",
                    "gist_url": "https://gist.github.com/test/123",
                }
            }
        }
        mock_subprocess.return_value = Mock(returncode=0)

        with patch("sys.argv", ["install_component.py", "test-agent"]):
            result = main()

        assert result == 0
        mock_subprocess.assert_called_once()

    @patch("scripts.install_component.load_local_registry")
    @patch("builtins.print")
    def test_main_component_not_found(self, mock_print: MagicMock, mock_load: MagicMock) -> None:
        """Test when component is not found in registry."""
        mock_load.return_value = {"components": {}}

        with patch("sys.argv", ["install_component.py", "nonexistent"]):
            result = main()

        assert result == 1
        assert any("not found" in str(call) for call in mock_print.call_args_list)

    @patch("scripts.install_component.load_local_registry")
    @patch("builtins.print")
    def test_main_component_missing_gist_url(
        self, mock_print: MagicMock, mock_load: MagicMock
    ) -> None:
        """Test when component has no gist_url."""
        mock_load.return_value = {
            "components": {
                "test-agent": {
                    "name": "test-agent",
                    "type": "agent",
                }
            }
        }

        with patch("sys.argv", ["install_component.py", "test-agent"]):
            result = main()

        assert result == 1
        assert any("no gist_url" in str(call) for call in mock_print.call_args_list)

    @patch("subprocess.run")
    @patch("scripts.install_component.load_local_registry")
    def test_main_installation_failure(
        self, mock_load: MagicMock, mock_subprocess: MagicMock
    ) -> None:
        """Test when installation subprocess fails."""
        mock_load.return_value = {
            "components": {
                "test-agent": {
                    "name": "test-agent",
                    "type": "agent",
                    "gist_url": "https://gist.github.com/test/123",
                }
            }
        }
        mock_subprocess.return_value = Mock(returncode=1)

        with patch("sys.argv", ["install_component.py", "test-agent"]):
            result = main()

        assert result == 1

    @patch("scripts.install_component.load_remote_registry")
    @patch("builtins.print")
    def test_main_from_registry_without_url(
        self, mock_print: MagicMock, mock_load: MagicMock
    ) -> None:
        """Test --from-registry without --registry-url."""
        with patch("sys.argv", ["install_component.py", "test", "--from-registry"]):
            result = main()

        assert result == 1
        assert any("required" in str(call) for call in mock_print.call_args_list)

    @patch("subprocess.run")
    @patch("scripts.install_component.load_remote_registry")
    def test_main_from_registry_with_url(
        self, mock_load: MagicMock, mock_subprocess: MagicMock
    ) -> None:
        """Test successful installation from remote registry."""
        mock_load.return_value = {
            "components": {
                "test-agent": {
                    "name": "test-agent",
                    "type": "agent",
                    "gist_url": "https://gist.github.com/test/123",
                }
            }
        }
        mock_subprocess.return_value = Mock(returncode=0)

        with patch(
            "sys.argv",
            [
                "install_component.py",
                "test-agent",
                "--from-registry",
                "--registry-url",
                "https://gist.github.com/registry/abc",
            ],
        ):
            result = main()

        assert result == 0
        mock_load.assert_called_once()

    @patch("scripts.install_component.load_remote_registry")
    @patch("builtins.print")
    def test_main_remote_registry_error(self, mock_print: MagicMock, mock_load: MagicMock) -> None:
        """Test handling of remote registry loading errors."""
        mock_load.side_effect = Exception("Network error")

        with patch(
            "sys.argv",
            [
                "install_component.py",
                "test",
                "--from-registry",
                "--registry-url",
                "https://gist.github.com/test/123",
            ],
        ):
            result = main()

        assert result == 1
        assert any("Failed to load" in str(call) for call in mock_print.call_args_list)


class TestInstallComponentIntegration:
    """Integration tests for install_component functionality."""

    def test_find_and_install_workflow(self, tmp_path: Path) -> None:
        """Test the complete workflow of finding and preparing to install."""
        # Create a mock registry
        registry_data = {
            "components": {
                "path/to/test-agent.md": {
                    "name": "test-agent",
                    "type": "agent",
                    "domain": "core",
                    "gist_url": "https://gist.github.com/test/123",
                    "description": "A test agent",
                }
            }
        }

        registry_file = tmp_path / ".gist-registry.json"
        registry_file.write_text(json.dumps(registry_data))

        # Load registry
        registry = load_local_registry(tmp_path)

        # Find component
        component = find_component(registry["components"], "test-agent")

        assert component is not None
        assert component["name"] == "test-agent"
        assert component["gist_url"] == "https://gist.github.com/test/123"
        assert component["type"] == "agent"
