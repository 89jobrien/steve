import re
import yaml
from pathlib import Path

def parse_all_frontmatter(content):
    """Extract all YAML frontmatter blocks from the beginning of the file."""
    frontmatter_blocks = []
    current_content = content

    while True:
        # Match a frontmatter block at the very beginning
        # We need to be careful about empty lines between blocks
        match = re.match(r"^\s*---\s*\n(.*?)\n---\s*\n", current_content, re.DOTALL)
        if match:
            frontmatter_str = match.group(1)
            try:
                data = yaml.safe_load(frontmatter_str) or {}
                frontmatter_blocks.append(data)
                # Remove the matched block and any leading whitespace for the next iteration
                current_content = current_content[match.end():].lstrip()
            except yaml.YAMLError:
                # If it's not valid YAML, it's probably a horizontal rule or just content
                break
        else:
            break

    return frontmatter_blocks, current_content

def fix_file(file_path):
    content = file_path.read_text(encoding="utf-8")
    blocks, body = parse_all_frontmatter(content)

    # Merge all blocks
    merged_frontmatter = {}
    for block in blocks:
        merged_frontmatter.update(block)

    # Ensure name
    if "name" not in merged_frontmatter:
        # Use filename stem
        merged_frontmatter["name"] = file_path.stem

    # Ensure description
    if "description" not in merged_frontmatter:
        # Try to find a description in the body (first paragraph or heading)
        # For agents, sometimes it's in a 'description' field in a second block
        # which we already merged.
        # If still missing, look at the body.
        match = re.search(r"^#+ .*

(.*)", body)
        if match:
            desc = match.group(1).strip().split('\n')[0]
            if len(desc) > 10: # Only if it looks like a real description
                merged_frontmatter["description"] = desc
            else:
                merged_frontmatter["description"] = f"Component in {file_path.parent.name}"
        else:
            merged_frontmatter["description"] = f"Component in {file_path.parent.name}"

    # Reconstruct the file
    new_frontmatter_yaml = yaml.dump(merged_frontmatter, default_flow_style=False, sort_keys=False)
    new_content = f"---\n{new_frontmatter_yaml}---\n\n{body}"

    if content != new_content:
        file_path.write_text(new_content, encoding="utf-8")
        return True
    return False

steve_dir = Path("steve")
# Include templates as well as they were in the audit
component_dirs = ["agents", "skills", "commands", "hooks", "templates"]

fixed_count = 0
for cdir in component_dirs:
    dir_path = steve_dir / cdir
    if not dir_path.exists():
        continue

    for file_path in dir_path.rglob("*.md"):
        if file_path.name == "README.md":
            continue

        try:
            if fix_file(file_path):
                fixed_count += 1
        except Exception as e:
            print(f"Error fixing {file_path}: {e}")

print(f"Fixed {fixed_count} files.")
