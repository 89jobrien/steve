"""Tests for python_to_markdown.py - Python to Markdown converter."""

from pathlib import Path
from unittest.mock import patch

import pytest

from scripts.python_to_markdown import filename_to_title, main, python_to_markdown


class TestFilenameToTitle:
    """Tests for filename_to_title function."""

    def test_simple_filename(self) -> None:
        """Test converting simple filename to title."""
        result = filename_to_title("test.py")

        assert result == "Test"

    def test_filename_with_underscores(self) -> None:
        """Test filename with underscores."""
        result = filename_to_title("test_module.py")

        assert result == "Test Module"

    def test_filename_with_dashes(self) -> None:
        """Test filename with dashes."""
        result = filename_to_title("test-module.py")

        assert result == "Test Module"

    def test_filename_with_mixed_separators(self) -> None:
        """Test filename with both dashes and underscores."""
        result = filename_to_title("test_module-helper.py")

        assert result == "Test Module Helper"

    def test_filename_multiple_words(self) -> None:
        """Test filename with multiple words."""
        result = filename_to_title("my_long_module_name.py")

        assert result == "My Long Module Name"

    def test_filename_already_titled(self) -> None:
        """Test filename that's already in title case."""
        result = filename_to_title("TestModule.py")

        assert result == "Testmodule"

    def test_filename_with_numbers(self) -> None:
        """Test filename with numbers."""
        result = filename_to_title("test_module_v2.py")

        assert result == "Test Module V2"

    def test_filename_empty_parts_ignored(self) -> None:
        """Test that empty parts from consecutive separators are ignored."""
        result = filename_to_title("test__module.py")

        assert result == "Test Module"


class TestPythonToMarkdown:
    """Tests for python_to_markdown function."""

    def test_convert_python_file_to_markdown(self, tmp_path: Path) -> None:
        """Test basic conversion of Python file to Markdown."""
        # Create test Python file
        python_file = tmp_path / "test.py"
        python_content = '''def hello():
    """Say hello."""
    print("Hello, World!")
'''
        python_file.write_text(python_content)

        # Convert to markdown
        python_to_markdown(str(python_file))

        # Check output file was created
        markdown_file = tmp_path / "test.md"
        assert markdown_file.exists()

        # Check content
        content = markdown_file.read_text()
        assert content.startswith("# Test\n\n```python\n")
        assert python_content in content
        assert content.endswith("```\n")

    def test_convert_with_custom_output_path(self, tmp_path: Path) -> None:
        """Test conversion with custom output path."""
        python_file = tmp_path / "source.py"
        python_file.write_text("print('test')")

        output_file = tmp_path / "custom_output.md"

        python_to_markdown(str(python_file), str(output_file))

        assert output_file.exists()
        content = output_file.read_text()
        assert "# Source" in content
        assert "print('test')" in content

    def test_convert_preserves_python_code(self, tmp_path: Path) -> None:
        """Test that Python code is preserved exactly."""
        python_file = tmp_path / "code.py"
        python_content = '''# Comment
def func(x: int) -> str:
    """Docstring."""
    return f"Value: {x}"

if __name__ == "__main__":
    func(42)
'''
        python_file.write_text(python_content)

        python_to_markdown(str(python_file))

        markdown_file = tmp_path / "code.md"
        content = markdown_file.read_text()

        # Verify all lines are preserved
        assert "# Comment" in content
        assert "def func(x: int) -> str:" in content
        assert '"""Docstring."""' in content
        assert 'return f"Value: {x}"' in content
        assert 'if __name__ == "__main__":' in content

    def test_convert_generates_title_from_filename(self, tmp_path: Path) -> None:
        """Test that title is correctly generated from filename."""
        python_file = tmp_path / "my_test_module.py"
        python_file.write_text("# Code")

        python_to_markdown(str(python_file))

        markdown_file = tmp_path / "my_test_module.md"
        content = markdown_file.read_text()

        assert content.startswith("# My Test Module\n")

    def test_convert_nonexistent_file_exits(self, tmp_path: Path) -> None:
        """Test that converting nonexistent file exits with error."""
        nonexistent_file = tmp_path / "nonexistent.py"

        with pytest.raises(SystemExit):
            python_to_markdown(str(nonexistent_file))

    def test_convert_empty_python_file(self, tmp_path: Path) -> None:
        """Test converting empty Python file."""
        python_file = tmp_path / "empty.py"
        python_file.write_text("")

        python_to_markdown(str(python_file))

        markdown_file = tmp_path / "empty.md"
        assert markdown_file.exists()
        content = markdown_file.read_text()

        assert content == "# Empty\n\n```python\n```\n"

    def test_convert_python_file_with_unicode(self, tmp_path: Path) -> None:
        """Test converting Python file with unicode characters."""
        python_file = tmp_path / "unicode.py"
        python_content = '''# -*- coding: utf-8 -*-
"""Unicode test: ™ © ® ♠ ♣ ♥ ♦"""

def greet(name: str) -> str:
    return f"Hello, {name}! 你好 🌍"
'''
        python_file.write_text(python_content, encoding="utf-8")

        python_to_markdown(str(python_file))

        markdown_file = tmp_path / "unicode.md"
        content = markdown_file.read_text(encoding="utf-8")

        assert "™ © ® ♠ ♣ ♥ ♦" in content
        assert "你好 🌍" in content


class TestMain:
    """Tests for main function."""

    def test_main_with_input_file(self, tmp_path: Path) -> None:
        """Test main function with input file."""
        python_file = tmp_path / "test.py"
        python_file.write_text("print('test')")

        with patch("sys.argv", ["python_to_markdown.py", str(python_file)]):
            main()

        markdown_file = tmp_path / "test.md"
        assert markdown_file.exists()

    def test_main_with_input_and_output_file(self, tmp_path: Path) -> None:
        """Test main function with both input and output files."""
        python_file = tmp_path / "input.py"
        python_file.write_text("print('test')")

        output_file = tmp_path / "output.md"

        with patch(
            "sys.argv",
            ["python_to_markdown.py", str(python_file), str(output_file)],
        ):
            main()

        assert output_file.exists()

    def test_main_without_arguments_exits(self) -> None:
        """Test main function without arguments exits with usage message."""
        with patch("sys.argv", ["python_to_markdown.py"]), pytest.raises(SystemExit):
            main()

    def test_main_prints_usage_on_no_args(self, capsys) -> None:
        """Test that usage message is printed when no args provided."""
        with patch("sys.argv", ["python_to_markdown.py"]), pytest.raises(SystemExit):
            main()

        captured = capsys.readouterr()
        assert "Usage:" in captured.err
        assert "python_to_markdown.py" in captured.err


class TestPythonToMarkdownIntegration:
    """Integration tests for python_to_markdown functionality."""

    def test_full_conversion_workflow(self, tmp_path: Path) -> None:
        """Test complete conversion workflow from Python to Markdown."""
        # Create a realistic Python module
        python_file = tmp_path / "data_processor.py"
        python_content = '''#!/usr/bin/env python3
"""Data processing module.

This module provides utilities for processing data.
"""

from typing import List


def process_data(data: List[int]) -> List[int]:
    """Process a list of integers.

    Args:
        data: List of integers to process

    Returns:
        Processed list of integers
    """
    return [x * 2 for x in data if x > 0]


def main() -> None:
    """Main entry point."""
    data = [1, -2, 3, -4, 5]
    result = process_data(data)
    print(f"Result: {result}")


if __name__ == "__main__":
    main()
'''
        python_file.write_text(python_content)

        # Convert using the function
        python_to_markdown(str(python_file))

        # Verify output
        markdown_file = tmp_path / "data_processor.md"
        assert markdown_file.exists()

        content = markdown_file.read_text()

        # Verify title
        assert content.startswith("# Data Processor\n")

        # Verify code block markers
        assert "```python\n" in content
        assert content.endswith("```\n")

        # Verify all code is present
        assert "def process_data(data: List[int]) -> List[int]:" in content
        assert "def main() -> None:" in content
        assert '"""Data processing module.' in content

    def test_batch_conversion_multiple_files(self, tmp_path: Path) -> None:
        """Test converting multiple Python files."""
        files = ["module1.py", "module2.py", "helper_utils.py"]

        for filename in files:
            python_file = tmp_path / filename
            python_file.write_text(f"# {filename}")
            python_to_markdown(str(python_file))

        # Verify all markdown files were created
        for filename in files:
            md_filename = filename.replace(".py", ".md")
            markdown_file = tmp_path / md_filename
            assert markdown_file.exists()

    def test_title_generation_various_formats(self, tmp_path: Path) -> None:
        """Test title generation for various filename formats."""
        test_cases = [
            ("simple.py", "# Simple\n"),
            ("two_words.py", "# Two Words\n"),
            ("three-word-name.py", "# Three Word Name\n"),
            ("mixed_dash-style.py", "# Mixed Dash Style\n"),
        ]

        for filename, expected_title in test_cases:
            python_file = tmp_path / filename
            python_file.write_text("pass")
            python_to_markdown(str(python_file))

            markdown_file = tmp_path / filename.replace(".py", ".md")
            content = markdown_file.read_text()

            assert content.startswith(expected_title)
