---
description: List all available skills with descriptions and usage information
allowed-tools: Bash, Read, Grep
argument-hint: '[--verbose] | [--used-by] | [--references]'
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: commands
---

# List Skills

Display all available skills in the `~/.claude/skills/` directory.

## Options

- `--verbose`: Show full descriptions
- `--used-by`: Show which agents use each skill
- `--references`: Show reference files for each skill

## Execution

```bash
echo "=== AVAILABLE SKILLS ==="
echo ""
for skill_dir in ~/.claude/skills/*/; do
  skill_name=$(basename "$skill_dir")
  if [ -f "$skill_dir/SKILL.md" ]; then
    # Extract description from frontmatter
    desc=$(grep -A1 "^description:" "$skill_dir/SKILL.md" 2>/dev/null | head -1 | sed 's/^description: //' | cut -c1-80)

    # Check for deprecated
    if grep -q "^deprecated: true" "$skill_dir/SKILL.md" 2>/dev/null; then
      echo "- [DEPRECATED] $skill_name"
    else
      echo "- $skill_name: $desc..."
    fi
  fi
done
echo ""
echo "Total: $(ls -d ~/.claude/skills/*/ 2>/dev/null | wc -l | tr -d ' ') skills"
```

## Usage Examples

```
/skills:list              # List all skills with short descriptions
/skills:list --verbose    # Show full descriptions
/skills:list --used-by    # Show agent associations
```
