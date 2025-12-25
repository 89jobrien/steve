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
                # Remove quotes if present
                if (value.startswith("'") and value.endswith("'")) or (value.startswith('"') and value.endswith('"')):
                    value = value[1:-1]
                result[key] = value
        return result


def parse_and_merge_frontmatter(content: str) -> tuple[dict, str]:
    """Parse frontmatter and merge multiple blocks into one."""
    # Double pattern - matches two consecutive frontmatter blocks
    double_pattern = re.compile(
        r"^---\s*\n(.*?)\n---\s*\n\s*---\s*\n(.*?)\n---\s*\n", re.DOTALL
    )

    # Single pattern
    single_pattern = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)

    double_match = double_pattern.match(content)
    if double_match:
        yaml1 = double_match.group(1)
        yaml2 = double_match.group(2)
        body = content[double_match.end() :]

        data1 = safe_yaml_load(yaml1)
        data2 = safe_yaml_load(yaml2)

        # Merge with data2 taking precedence (it has the actual config)
        merged = data1.copy()
        merged.update(data2)
        return merged, body

    single_match = single_pattern.match(content)
    if single_match:
        yaml1 = single_match.group(1)
        body = content[single_match.end() :]
        data = safe_yaml_load(yaml1)
        return data, body

    return {}, content

def extract_description_from_body(body):
    # Look for heading followed by text
    match = re.search(r"^#+ .*\n\n(.*)", body, re.MULTILINE)
    if match:
        desc = match.group(1).strip()
        if len(desc) > 10 and not desc.startswith('!['):
             return desc.split('\n')[0]

    match = re.search(r"^(You are .*|This agent .*)", body, re.MULTILINE)
    if match:
        return match.group(1).strip()

    return "Agent configuration."

def fix_agent_file(file_path):
    content = file_path.read_text(encoding="utf-8")
    merged_data, body = parse_and_merge_frontmatter(content)
    merged_data["name"] = file_path.stem

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
    agents_dir = Path("steve/agents")
    count = 0
    if not agents_dir.exists():
        return

    for f in agents_dir.rglob("*.md"):
        if f.name == "README.md":
            continue
        try:
            if fix_agent_file(f):
                count += 1
        except Exception as e:
            print(f"Error {f}: {e}")

    print(f"Total Agents Fixed: {count}")

if __name__ == "__main__":
    main()
