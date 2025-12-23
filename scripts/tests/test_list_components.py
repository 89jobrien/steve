"""Tests for list_components.py - Listing components from registry."""

import json
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

from scripts.list_components import (
    filter_components,
    load_local_registry,
    load_remote_registry,
    main,
    print_components,
)


class TestLoadLocalRegistry:
    """Tests for load_local_registry function."""

    def test_load_existing_registry(self, tmp_path: Path) -> None:
        """Test loading an existing local registry file."""
        registry_data = {
            "components": {
                "agent1.md": {
                    "name": "agent1",
                    "type": "agent",
                }
            }
        }

        registry_file = tmp_path / ".gist-registry.json"
        registry_file.write_text(json.dumps(registry_data))

        result = load_local_registry(tmp_path)

        assert result == registry_data

    def test_load_nonexistent_registry(self, tmp_path: Path) -> None:
        """Test loading when registry file doesn't exist."""
        result = load_local_registry(tmp_path)

        assert result == {"components": {}}


class TestLoadRemoteRegistry:
    """Tests for load_remote_registry function."""

    @patch("requests.get")
    def test_load_remote_registry_success(self, mock_get: MagicMock) -> None:
        """Test successful loading of remote registry."""
        registry_data = {"components": {"test": {"name": "test"}}}

        mock_response = Mock()
        mock_response.json.return_value = {
            "files": {"registry.json": {"content": json.dumps(registry_data)}}
        }
        mock_get.return_value = mock_response

        result = load_remote_registry("https://gist.github.com/user/123")

        assert result == registry_data


class TestFilterComponents:
    """Tests for filter_components function."""

    def test_filter_no_filters_returns_all(self) -> None:
        """Test that no filters returns all components sorted by name."""
        components = {
            "path1": {"name": "zebra", "type": "agent"},
            "path2": {"name": "alpha", "type": "command"},
        }

        result = filter_components(components)

        assert len(result) == 2
        # Should be sorted by name
        assert result[0]["name"] == "alpha"
        assert result[1]["name"] == "zebra"

    def test_filter_by_type(self) -> None:
        """Test filtering by component type."""
        components = {
            "agent.md": {"name": "agent1", "type": "agent"},
            "command.md": {"name": "command1", "type": "command"},
            "skill.md": {"name": "skill1", "type": "skill"},
        }

        result = filter_components(components, component_type="agent")

        assert len(result) == 1
        assert result[0]["type"] == "agent"

    def test_filter_by_domain(self) -> None:
        """Test filtering by domain."""
        components = {
            "core.md": {"name": "agent1", "type": "agent", "domain": "core"},
            "dev.md": {"name": "agent2", "type": "agent", "domain": "development"},
        }

        result = filter_components(components, domain="development")

        assert len(result) == 1
        assert result[0]["domain"] == "development"

    def test_filter_by_search_in_name(self) -> None:
        """Test searching in component name."""
        components = {
            "test-agent.md": {"name": "test-agent", "type": "agent", "description": ""},
            "other-agent.md": {"name": "other-agent", "type": "agent", "description": ""},
        }

        result = filter_components(components, search="test")

        assert len(result) == 1
        assert result[0]["name"] == "test-agent"

    def test_filter_by_search_in_description(self) -> None:
        """Test searching in component description."""
        components = {
            "agent1.md": {"name": "agent1", "type": "agent", "description": "handles testing"},
            "agent2.md": {"name": "agent2", "type": "agent", "description": "other functionality"},
        }

        result = filter_components(components, search="testing")

        assert len(result) == 1
        assert result[0]["name"] == "agent1"

    def test_filter_by_search_in_path(self) -> None:
        """Test searching in component path."""
        components = {
            "test/path/agent.md": {"name": "agent", "type": "agent", "description": ""},
            "other/path/agent2.md": {"name": "agent2", "type": "agent", "description": ""},
        }

        result = filter_components(components, search="test/path")

        assert len(result) == 1
        assert result[0]["name"] == "agent"

    def test_filter_search_case_insensitive(self) -> None:
        """Test that search is case insensitive."""
        components = {
            "TestAgent.md": {"name": "TestAgent", "type": "agent", "description": ""},
        }

        result = filter_components(components, search="testagent")

        assert len(result) == 1

    def test_filter_multiple_criteria(self) -> None:
        """Test filtering with multiple criteria."""
        components = {
            "agent1.md": {
                "name": "test-agent",
                "type": "agent",
                "domain": "core",
                "description": "testing",
            },
            "agent2.md": {
                "name": "other-agent",
                "type": "agent",
                "domain": "core",
                "description": "other",
            },
            "command1.md": {
                "name": "test-command",
                "type": "command",
                "domain": "core",
                "description": "testing",
            },
        }

        result = filter_components(
            components,
            component_type="agent",
            domain="core",
            search="test",
        )

        assert len(result) == 1
        assert result[0]["name"] == "test-agent"

    def test_filter_returns_empty_when_no_matches(self) -> None:
        """Test that empty list is returned when no components match."""
        components = {
            "agent.md": {"name": "agent", "type": "agent", "description": ""},
        }

        result = filter_components(components, component_type="command")

        assert len(result) == 0


class TestPrintComponents:
    """Tests for print_components function."""

    @patch("builtins.print")
    def test_print_components_empty_list(self, mock_print: MagicMock) -> None:
        """Test printing empty component list."""
        print_components([])

        assert any("No components" in str(call) for call in mock_print.call_args_list)

    @patch("builtins.print")
    def test_print_components_basic_info(self, mock_print: MagicMock) -> None:
        """Test printing basic component information."""
        components = [
            {
                "name": "test-agent",
                "type": "agent",
                "description": "A test agent",
                "domain": "core",
                "gist_url": "https://gist.github.com/test/123",
            }
        ]

        print_components(components)

        printed_output = " ".join(str(call) for call in mock_print.call_args_list)
        assert "test-agent" in printed_output
        assert "agent" in printed_output
        assert "A test agent" in printed_output

    @patch("builtins.print")
    def test_print_components_truncates_long_description(self, mock_print: MagicMock) -> None:
        """Test that long descriptions are truncated."""
        long_description = "a" * 100

        components = [
            {
                "name": "test",
                "type": "agent",
                "description": long_description,
            }
        ]

        print_components(components)

        printed_output = " ".join(str(call) for call in mock_print.call_args_list)
        assert "..." in printed_output

    @patch("builtins.print")
    def test_print_components_with_details(self, mock_print: MagicMock) -> None:
        """Test printing with detailed information."""
        components = [
            {
                "name": "test",
                "type": "agent",
                "description": "Test",
                "path": "steve/agents/core/test.md",
                "published_at": "2025-01-01",
            }
        ]

        print_components(components, show_details=True)

        printed_output = " ".join(str(call) for call in mock_print.call_args_list)
        assert "Path:" in printed_output
        assert "Published:" in printed_output

    @patch("builtins.print")
    def test_print_components_multiple(self, mock_print: MagicMock) -> None:
        """Test printing multiple components."""
        components = [
            {"name": "agent1", "type": "agent", "description": "First"},
            {"name": "agent2", "type": "agent", "description": "Second"},
        ]

        print_components(components)

        printed_output = " ".join(str(call) for call in mock_print.call_args_list)
        assert "agent1" in printed_output
        assert "agent2" in printed_output
        assert "Found 2" in printed_output


class TestMain:
    """Tests for main function."""

    @patch("scripts.list_components.load_local_registry")
    @patch("scripts.list_components.print_components")
    def test_main_list_all_components(self, mock_print: MagicMock, mock_load: MagicMock) -> None:
        """Test listing all components from local registry."""
        mock_load.return_value = {
            "components": {
                "test.md": {"name": "test", "type": "agent", "description": "Test agent"}
            }
        }

        with patch("sys.argv", ["list_components.py"]):
            result = main()

        assert result == 0
        mock_print.assert_called_once()

    @patch("scripts.list_components.load_local_registry")
    @patch("scripts.list_components.print_components")
    def test_main_filter_by_type(self, mock_print: MagicMock, mock_load: MagicMock) -> None:
        """Test filtering by type via command line."""
        mock_load.return_value = {
            "components": {
                "agent.md": {"name": "agent", "type": "agent", "description": ""},
                "command.md": {"name": "command", "type": "command", "description": ""},
            }
        }

        with patch("sys.argv", ["list_components.py", "--type", "agent"]):
            result = main()

        assert result == 0
        # Verify only agent was passed to print_components
        printed_components = mock_print.call_args[0][0]
        assert len(printed_components) == 1
        assert printed_components[0]["type"] == "agent"

    @patch("scripts.list_components.load_local_registry")
    @patch("scripts.list_components.print_components")
    def test_main_search_filter(self, mock_print: MagicMock, mock_load: MagicMock) -> None:
        """Test search filtering via command line."""
        mock_load.return_value = {
            "components": {
                "test1.md": {"name": "test-agent", "type": "agent", "description": ""},
                "other.md": {"name": "other", "type": "agent", "description": ""},
            }
        }

        with patch("sys.argv", ["list_components.py", "--search", "test"]):
            result = main()

        assert result == 0
        printed_components = mock_print.call_args[0][0]
        assert len(printed_components) == 1
        assert printed_components[0]["name"] == "test-agent"

    @patch("scripts.list_components.load_remote_registry")
    @patch("scripts.list_components.print_components")
    def test_main_from_registry(self, mock_print: MagicMock, mock_load: MagicMock) -> None:
        """Test loading from remote registry."""
        mock_load.return_value = {
            "components": {"test.md": {"name": "test", "type": "agent", "description": ""}}
        }

        with patch(
            "sys.argv",
            [
                "list_components.py",
                "--from-registry",
                "--registry-url",
                "https://gist.github.com/test/123",
            ],
        ):
            result = main()

        assert result == 0
        mock_load.assert_called_once()

    @patch("builtins.print")
    def test_main_from_registry_without_url(self, mock_print: MagicMock) -> None:
        """Test error when --from-registry used without --registry-url."""
        with patch("sys.argv", ["list_components.py", "--from-registry"]):
            result = main()

        assert result == 1
        assert any("required" in str(call) for call in mock_print.call_args_list)

    @patch("scripts.list_components.load_remote_registry")
    @patch("builtins.print")
    def test_main_remote_registry_error(self, mock_print: MagicMock, mock_load: MagicMock) -> None:
        """Test handling of remote registry loading errors."""
        mock_load.side_effect = Exception("Network error")

        with patch(
            "sys.argv",
            [
                "list_components.py",
                "--from-registry",
                "--registry-url",
                "https://gist.github.com/test/123",
            ],
        ):
            result = main()

        assert result == 1
        assert any("Failed to load" in str(call) for call in mock_print.call_args_list)

    @patch("scripts.list_components.load_local_registry")
    @patch("scripts.list_components.print_components")
    def test_main_with_details_flag(self, mock_print: MagicMock, mock_load: MagicMock) -> None:
        """Test --details flag passes show_details to print function."""
        mock_load.return_value = {
            "components": {"test.md": {"name": "test", "type": "agent", "description": ""}}
        }

        with patch("sys.argv", ["list_components.py", "--details"]):
            result = main()

        assert result == 0
        # Verify show_details=True was passed
        assert mock_print.call_args[1]["show_details"] is True


class TestListComponentsIntegration:
    """Integration tests for list_components functionality."""

    def test_filter_and_print_workflow(self, tmp_path: Path) -> None:
        """Test complete workflow of loading, filtering, and preparing to print."""
        # Create mock registry
        registry_data = {
            "components": {
                "agent1.md": {
                    "name": "test-agent",
                    "type": "agent",
                    "domain": "core",
                    "description": "A test agent for testing",
                },
                "agent2.md": {
                    "name": "other-agent",
                    "type": "agent",
                    "domain": "development",
                    "description": "Another agent",
                },
                "command1.md": {
                    "name": "test-command",
                    "type": "command",
                    "description": "A test command",
                },
            }
        }

        registry_file = tmp_path / ".gist-registry.json"
        registry_file.write_text(json.dumps(registry_data))

        # Load registry
        registry = load_local_registry(tmp_path)

        # Filter by type
        filtered = filter_components(registry["components"], component_type="agent")
        assert len(filtered) == 2

        # Filter by search
        search_filtered = filter_components(registry["components"], search="test")
        assert len(search_filtered) == 2  # test-agent and test-command

        # Filter by multiple criteria
        specific = filter_components(
            registry["components"],
            component_type="agent",
            search="test",
        )
        assert len(specific) == 1
        assert specific[0]["name"] == "test-agent"
