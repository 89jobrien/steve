---
description: Search skills by keyword in name, description, or content
allowed-tools: Bash, Read, Grep
argument-hint: '[keyword]'
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: commands
name: search
---

# Search Skills

Search for skills matching a keyword in their name, description, or content.

## Arguments

- `<keyword>`: The search term to find in skill names and descriptions

## Execution

Search for skills matching the provided keyword:

```bash
keyword="$ARGUMENTS"
if [ -z "$keyword" ]; then
  echo "Usage: /skills:search <keyword>"
  echo "Example: /skills:search database"
  exit 1
fi

echo "=== SKILLS MATCHING: $keyword ==="
echo ""

for skill_dir in ~/.claude/skills/*/; do
  skill_name=$(basename "$skill_dir")
  skill_file="$skill_dir/SKILL.md"

  if [ -f "$skill_file" ]; then
    # Search in name and content
    if echo "$skill_name" | grep -qi "$keyword" || grep -qi "$keyword" "$skill_file" 2>/dev/null; then
      desc=$(grep -A1 "^description:" "$skill_file" 2>/dev/null | head -1 | sed 's/^description: //' | cut -c1-80)
      echo "- $skill_name: $desc..."
    fi
  fi
done
```

## Usage Examples

```
/skills:search database    # Find database-related skills
/skills:search testing     # Find testing-related skills
/skills:search security    # Find security-related skills
```
