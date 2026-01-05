"""Fix hook metadata by ensuring name and description fields are present."""

import re
from pathlib import Path

import yaml


def safe_yaml_load(yaml_text: str) -> dict:
    """Load YAML safely, handling problematic values."""
    try:
        return yaml.safe_load(yaml_text) or {}
    except yaml.YAMLError:
        # Try line-by-line parsing for problematic YAML
        result = {}
        for line in yaml_text.strip().split("\n"):
            if ":" in line and not line.startswith(" "):
                key, _, value = line.partition(":")
                key = key.strip()
                value = value.strip()
                # Strip quotes
                if (value.startswith("'") and value.endswith("'")) or (
                    value.startswith('"') and value.endswith('"')
                ):
                    value = value[1:-1]
                result[key] = value
        return result


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Parse YAML frontmatter from markdown content."""
    if not content.startswith("---"):
        return {}, content

    # Find the closing ---
    end_match = re.search(r"\n---\s*\n", content[3:])
    if not end_match:
        return {}, content

    fm_end = end_match.end() + 3
    yaml_text = content[3 : end_match.start() + 3]
    body = content[fm_end:]

    metadata = safe_yaml_load(yaml_text)
    return metadata, body


def extract_name_from_body(body: str, filename: str) -> str:
    """Extract name from the body content or filename."""
    # Try to get first heading text
    heading_match = re.search(r"^#+ (.+)$", body, re.MULTILINE)
    if heading_match:
        heading = heading_match.group(1).strip()
        # Convert to kebab-case name
        name = heading.lower()
        name = re.sub(r"[^a-z0-9]+", "-", name)
        name = name.strip("-")
        if name:
            return name

    # Fall back to filename
    return filename.replace(".md", "").replace("_", "-")


def extract_description_from_body(body: str) -> str:
    """Extract description from the body content."""
    # Look for docstring in Python code block
    docstring_match = re.search(r'```python\n.*?"""(.*?)"""', body, re.DOTALL | re.MULTILINE)
    if docstring_match:
        docstring = docstring_match.group(1).strip()
        # Get first line/sentence of docstring
        first_line = docstring.split("\n")[0].strip()
        if first_line and len(first_line) > 10:
            return first_line

    # Look for description after heading
    heading_match = re.search(r"^#+ .+$", body, re.MULTILINE)
    if heading_match:
        after_heading = body[heading_match.end() :].lstrip()
        # Get first paragraph
        para_match = re.match(r"^([^#\n`].+?)(?:\n\n|\n#|\n```|$)", after_heading, re.DOTALL)
        if para_match:
            para = para_match.group(1).strip()
            if len(para) > 20 and not para.startswith("!"):
                first_sentence = para.split(". ")[0].split("\n")[0]
                if len(first_sentence) > 10:
                    return first_sentence.rstrip(".")

    # Get first heading as description
    if heading_match:
        heading = heading_match.group(0).lstrip("#").strip()
        if len(heading) > 5:
            return f"{heading} hook implementation"

    return "Hook implementation."


def fix_hook_file(file_path: Path) -> bool:
    """Fix a single hook file's metadata. Returns True if modified."""
    content = file_path.read_text()
    metadata, body = parse_frontmatter(content)

    if not metadata:
        # No frontmatter found, skip
        return False

    modified = False
    filename = file_path.stem

    # Check and add name if missing
    if "name" not in metadata:
        name = extract_name_from_body(body, filename)
        metadata["name"] = name
        modified = True

    # Check and add description if missing
    if "description" not in metadata:
        description = extract_description_from_body(body)
        metadata["description"] = description
        modified = True

    if modified:
        # Rebuild the file with updated frontmatter
        # Preserve key order: name, description first, then others
        ordered_keys = []
        if "name" in metadata:
            ordered_keys.append("name")
        if "description" in metadata:
            ordered_keys.append("description")
        for key in metadata:
            if key not in ordered_keys:
                ordered_keys.append(key)

        # Build YAML manually to preserve formatting
        yaml_lines = []
        for key in ordered_keys:
            value = metadata[key]
            # Quote string values with special chars
            needs_quotes = isinstance(value, str) and (
                any(c in value for c in [":", "#", "[", "]", "{", "}", ",", "'", '"'])
                or value.startswith("$")
            )
            if needs_quotes:
                value = f"'{value}'"
            yaml_lines.append(f"{key}: {value}")

        new_content = "---\n" + "\n".join(yaml_lines) + "\n---\n" + body
        file_path.write_text(new_content)
        return True

    return False


def main() -> None:
    """Fix metadata for all hook files."""
    hooks_dir = Path("steve/hooks")
    if not hooks_dir.exists():
        print("steve/hooks directory not found")
        return

    fixed_count = 0
    for md_file in hooks_dir.rglob("*.md"):
        # Skip README, __init__, and test files
        if md_file.name in ("README.md", "__init__.md"):
            continue
        if "tests" in md_file.parts:
            continue

        if fix_hook_file(md_file):
            print(f"Fixed: {md_file}")
            fixed_count += 1

    print(f"\nTotal Hooks Fixed: {fixed_count}")


if __name__ == "__main__":
    main()
