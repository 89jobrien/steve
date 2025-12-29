import re
import yaml
from pathlib import Path

def parse_all_frontmatter(content):
    frontmatter_blocks = []
    current_content = content

    while True:
        match = re.match(r"^\s*---\s*\n(.*?)\n---\s*\n", current_content, re.DOTALL)
        if match:
            frontmatter_str = match.group(1)
            try:
                data = yaml.safe_load(frontmatter_str) or {}
                frontmatter_blocks.append(data)
                current_content = current_content[match.end():].lstrip()
            except yaml.YAMLError:
                break
        else:
            break

    return frontmatter_blocks, current_content

def extract_description(body):
    # 1. Try to find a paragraph after a heading
    # Regex for heading followed by blank line and then text
    heading_pattern = r"^#+ .*

(.*)"
    match = re.search(heading_pattern, body, re.MULTILINE)
    if match:
        desc = match.group(1).strip()
        if len(desc) > 10 and not desc.startswith('!['):
            return desc.split('\n')[0]

    # 2. Try to find the first paragraph that isn't a heading
    match = re.search(r"^(?!#)(.*)", body, re.MULTILINE)
    if match:
        desc = match.group(1).strip()
        if len(desc) > 10 and not desc.startswith('!['):
            return desc.split('\n')[0]

    return "No description provided."

def fix_file(file_path, component_type):
    content = file_path.read_text(encoding="utf-8")
    blocks, body = parse_all_frontmatter(content)

    merged_frontmatter = {}
    for block in blocks:
        merged_frontmatter.update(block)

    merged_frontmatter["name"] = file_path.stem

    if "description" not in merged_frontmatter or not merged_frontmatter["description"]:
        merged_frontmatter["description"] = extract_description(body)

    new_frontmatter_yaml = yaml.dump(merged_frontmatter, default_flow_style=False, sort_keys=False)
    new_content = f"---\n{new_frontmatter_yaml}---\n\n{body}"

    if content != new_content:
        file_path.write_text(new_content, encoding="utf-8")
        return True
    return False

def main():
    base_dir = Path("steve")
    targets = {
        "agents": "Agent",
        "commands": "Command",
        "skills": "Skill",
        "hooks": "Hook"
    }

    fixed_count = 0

    for dir_name, c_type in targets.items():
        dir_path = base_dir / dir_name
        if not dir_path.exists(): continue

        for f in dir_path.rglob("*.md"):
            if f.name == "README.md": continue
            if dir_name == "skills" and f.name != "SKILL.md": continue

            try:
                if fix_file(f, c_type):
                    fixed_count += 1
            except Exception as e:
                print(f"Failed to fix {f}: {e}")

    print(f"Successfully fixed {fixed_count} files.")

if __name__ == "__main__":
    main()
