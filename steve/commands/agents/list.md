---
description: List all available agents organized by category with descriptions
allowed-tools: Bash, Read, Grep
argument-hint: '[--category <name>] | [--skills] | [--verbose]'
author: Joseph OBrien
status: unpublished
updated: '2025-12-23'
version: 1.0.1
tag: commands
---

# List Agents

Display all available agents in the `~/.claude/agents/` directory organized by category.

## Options

- `--category <name>`: Filter to specific category (e.g., dev, database, testing)
- `--skills`: Show which skills each agent uses
- `--verbose`: Show full descriptions and tools

## Execution

```bash
echo "=== AVAILABLE AGENTS ==="
echo ""

# Get all categories
for category in ~/.claude/agents/*/; do
  if [ -d "$category" ]; then
    cat_name=$(basename "$category")
    echo "### $cat_name"
    echo ""

    # List agents in category
    for agent in "$category"*.md; do
      if [ -f "$agent" ]; then
        name=$(grep "^name:" "$agent" 2>/dev/null | head -1 | sed 's/name: //')
        desc=$(grep "^description:" "$agent" 2>/dev/null | head -1 | sed 's/description: //' | cut -c1-70)
        skills=$(grep "^skills:" "$agent" 2>/dev/null | head -1 | sed 's/skills: //')

        if [ -n "$name" ]; then
          echo "- **$name**: $desc..."
          if [ -n "$skills" ] && [ "$skills" != "-" ]; then
            echo "  Skills: $skills"
          fi
        fi
      fi
    done
    echo ""
  fi
done

# Also check root agents
echo "### root"
echo ""
for agent in ~/.claude/agents/*.md; do
  if [ -f "$agent" ]; then
    name=$(grep "^name:" "$agent" 2>/dev/null | head -1 | sed 's/name: //')
    desc=$(grep "^description:" "$agent" 2>/dev/null | head -1 | sed 's/description: //' | cut -c1-70)

    if [ -n "$name" ]; then
      echo "- **$name**: $desc..."
    fi
  fi
done

echo ""
echo "Total: $(find ~/.claude/agents -name '*.md' -type f | wc -l | tr -d ' ') agents"
```

## Usage Examples

```
/agents:list                    # List all agents by category
/agents:list --category database  # Show only database agents
/agents:list --skills           # Show skills used by each agent
```

## Categories

Common agent categories:

- `ai-specialists` - AI/ML focused agents
- `code-quality` - Code review and quality
- `data-ai` - Data science and engineering
- `database` - Database specialists
- `deep-research-team` - Research orchestration
- `development-team` - Full-stack development
- `development-tools` - Dev tooling
- `devops-infrastructure` - DevOps and cloud
- `documentation` - Documentation writers
- `expert-advisors` - Domain experts
- `performance-testing` - Performance optimization
- `programming-languages` - Language specialists
- `testing` - Test automation
- `web-tools` - Web development
