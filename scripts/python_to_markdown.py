#!/usr/bin/env python3
"""
Convert a Python file to Markdown format.

Takes a Python file, adds a title heading based on the filename,
and wraps the code in markdown code fences.
"""

import re
import sys
from pathlib import Path


def filename_to_title(filename: str) -> str:
    """Convert filename to title case heading."""
    # Remove extension
    name = Path(filename).stem

    # Split on dashes and underscores
    parts = re.split(r"[-_]", name)

    # Title case each part and join with spaces
    return " ".join(part.title() for part in parts if part)


def python_to_markdown(input_file: str, output_file: str | None = None) -> None:
    """Convert Python file to Markdown format."""
    input_path = Path(input_file)

    if not input_path.exists():
        print(f"Error: File '{input_file}' not found.", file=sys.stderr)
        sys.exit(1)

    # Generate title from filename
    title = filename_to_title(input_file)

    # Read Python file content
    code_content = input_path.read_text(encoding="utf-8")

    # Determine output file
    output_path = input_path.with_suffix(".md") if output_file is None else Path(output_file)

    # Create markdown content
    markdown_content = f"# {title}\n\n```python\n{code_content}```\n"

    # Write markdown file
    output_path.write_text(markdown_content, encoding="utf-8")

    print(f"Converted '{input_file}' to '{output_path}'")


def main() -> None:
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage: python_to_markdown.py <input_file> [output_file]", file=sys.stderr)
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None

    python_to_markdown(input_file, output_file)


if __name__ == "__main__":
    main()
