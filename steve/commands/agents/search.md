---
description: Search agents by keyword in name, description, or skills
allowed-tools: Bash, Read, Grep
argument-hint: '[keyword]'
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: commands
---

# Search Agents

Search for agents matching a keyword in their name, description, or skills.

## Arguments

- `[keyword]`: The search term to find in agent names, descriptions, and skills

## Execution

Search for agents matching the provided keyword:

```bash
keyword="$ARGUMENTS"
if [ -z "$keyword" ]; then
  echo "Usage: /agents:search <keyword>"
  echo ""
  echo "Examples:"
  echo "  /agents:search database    # Find database-related agents"
  echo "  /agents:search python      # Find Python specialists"
  echo "  /agents:search security    # Find security agents"
  echo "  /agents:search testing     # Find testing agents"
  exit 1
fi

echo "=== AGENTS MATCHING: $keyword ==="
echo ""

find ~/.claude/agents -name "*.md" -type f | while read agent; do
  name=$(grep "^name:" "$agent" 2>/dev/null | head -1 | sed 's/name: //')

  if [ -n "$name" ]; then
    # Search in name, description, and content
    if echo "$name" | grep -qi "$keyword" || grep -qi "$keyword" "$agent" 2>/dev/null; then
      category=$(dirname "$agent" | xargs basename)
      desc=$(grep "^description:" "$agent" 2>/dev/null | head -1 | sed 's/description: //' | cut -c1-70)
      skills=$(grep "^skills:" "$agent" 2>/dev/null | head -1 | sed 's/skills: //')

      echo "- **$name** [$category]"
      echo "  $desc..."
      if [ -n "$skills" ] && [ "$skills" != "-" ]; then
        echo "  Skills: $skills"
      fi
      echo ""
    fi
  fi
done
```

## Usage Examples

```
/agents:search database    # Find database-related agents
/agents:search python      # Find Python specialists
/agents:search security    # Find security agents
/agents:search testing     # Find testing agents
/agents:search docker      # Find Docker/container agents
/agents:search react       # Find React specialists
```

## Tips

- Search is case-insensitive
- Searches agent name, description, and full content
- Results show category in brackets for context
- Skills are displayed when available
