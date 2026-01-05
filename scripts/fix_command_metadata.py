import re
from pathlib import Path

import yaml


def parse_and_merge_frontmatter(content):
    # Double pattern
    double_pattern = re.compile(r"^---\s*\n(.*?)\n---\s*\n\s*---\s*\n(.*?)\n---\s*\n", re.DOTALL)

    # Single pattern
    single_pattern = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

    double_match = double_pattern.match(content)
    if double_match:
        yaml1 = double_match.group(1)
        yaml2 = double_match.group(2)
        body = content[double_match.end() :]

        data1 = yaml.safe_load(yaml1) or {}
        data2 = yaml.safe_load(yaml2) or {}

        merged = data1.copy()
        merged.update(data2)
        return merged, body

    single_match = single_pattern.match(content)
    if single_match:
        yaml1 = single_match.group(1)
        body = content[single_match.end() :]
        data = yaml.safe_load(yaml1) or {}
        return data, body

    return {}, content


def extract_description_from_body(body):
    # 1. H1 title + optional description
    # # Command Name
    # Description here
    match = re.search(r"^#+ .*\n\n(.*)", body, re.MULTILINE)
    if match:
        desc = match.group(1).strip()
        if len(desc) > 10 and not desc.startswith("!["):
            return desc.split("\n")[0]

    # 2. First paragraph
    match = re.search(r"^(?!#)(.*)", body, re.MULTILINE)
    if match:
        desc = match.group(1).strip()
        if len(desc) > 10:
            return desc.split("\n")[0]

    return "Command configuration."


def fix_command_file(file_path):
    content = file_path.read_text(encoding="utf-8")
    merged_data, body = parse_and_merge_frontmatter(content)

    # Validation & Enrichment
    merged_data["name"] = file_path.stem

    # Preserve existing specific fields if present, otherwise ignore
    # allowed-tools, argument-hint are optional

    if "description" not in merged_data or not merged_data["description"]:
        merged_data["description"] = extract_description_from_body(body)

    new_yaml = yaml.dump(merged_data, default_flow_style=False, sort_keys=False)
    new_content = f"---\n{new_yaml}---\n\n{body}"

    if content != new_content:
        file_path.write_text(new_content, encoding="utf-8")
        print(f"Fixed: {file_path.name}")
        return True
    return False


def main():
    commands_dir = Path("steve/commands")
    count = 0
    if not commands_dir.exists():
        return

    for f in commands_dir.rglob("*.md"):
        if f.name == "README.md":
            continue
        try:
            if fix_command_file(f):
                count += 1
        except Exception as e:
            print(f"Error {f}: {e}")

    print(f"Total Commands Fixed: {count}")


if __name__ == "__main__":
    main()
